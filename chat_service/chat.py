import json
from flask import Flask, request, jsonify, make_response
import pika
import config

from DB_connections import connections


class Verification:
    def __init__(self, message, token, receiver):
        self.message = message
        self.token = token
        self.receiver = receiver

    def __verify_data__(self):
        con = connections.connection()
        if not self.message:
            return False

        try:
            cursor = con.cursor()
            cursor.execute(f"SELECT login, token_number "
                           f"FROM users "
                           f"WHERE token_number = '{self.token}';")
            result = cursor.fetchall()
            if not str(result[0][1]) == self.token:
                return False
        except Exception:
            return False

        try:
            cursor = con.cursor()
            cursor.execute(f"SELECT login "
                           f"FROM users "
                           f"WHERE login = '{self.receiver}';")
            result = cursor.fetchall()
            if not result[0][0]:
                return False
        except:
            return False
        return True


class StartChat:
    def __init__(self, adress, port):
        self.adress = adress
        self.port = port
        app = Flask(__name__)

        @app.route("/send_message/", methods=["POST"])
        def receive_message():
            """
            Принимаем от клиента сообщение, его токен, логин адресата и дату/время отправки.
            Токен сверяем с БД. Если корректный:
            Подключаемся к очереди RabbitMQ, кладем в очередь с названием логина адресата сообщение
            и дату/время его отправки в JSON формате.
            :return:
            """
            message = request.form['message']
            token = request.form["token"]
            receiver = request.form["receiver"]
            time = request.form["time"]

            verify_message = Verification(message, token, receiver)
            if verify_message.__verify_data__():

                credentials = pika.PlainCredentials('guest', 'guest')
                connection = pika.BlockingConnection(pika.ConnectionParameters(config.rabbit_adress,
                                                                               config.rabbit_port,
                                                                               '/',
                                                                               credentials))
                channel = connection.channel()
                con = connections.connection()
                cursor = con.cursor()
                cursor.execute(f"SELECT login, user_id "
                               f"FROM messenger.users "
                               f"WHERE token_number = '{token}';")
                result = cursor.fetchall()
                login = result[0][0]
                sender_id = result[0][1]
                cursor.execute(f"SELECT user_id "
                               f"FROM messenger.users "
                               f"WHERE login = '{receiver}';")
                receiver_id = cursor.fetchall()[0][0]
                try:
                    cursor.execute(
                        f"INSERT INTO messenger.messages (sender_id, receiver_id, message, send_time, received)"
                        f" VALUES ('{sender_id}', '{receiver_id}', '{message}', '{time}', '{False}');"
                    )
                    con.commit()
                    print("Сообщение успешно добавлено в базу!")
                except Exception:
                    print("Не удалось записать сообщение в базу!")

                channel.queue_declare(queue=login)
                package = json.dumps({
                    'sender': login,
                    'date': time,
                    'message': message
                })
                channel.basic_publish(exchange='', routing_key=login, body=package)
                connection.close()
                return make_response(jsonify([str("Successfully send!"), 200]))
            else:
                return make_response(jsonify([str("Wrong request!"), 400]))

        @app.route("/give_message/", methods=["GET"])
        def give_message():
            """
            Выдаем клиенту сообщение по его токену из очереди сообщений
            По моей идее, клиент регулярно посылает POST запрос на сервер, запрашивая новые сообщения для него.
            в этом запросе он передает свой токен (поэтому пост запрос, т.к. токен не должен быть в урле)
            :return:
            """
            token = request.args.get('token')
            con = connections.connection()
            cursor = con.cursor()
            cursor.execute("SELECT login "
                           "FROM users "
                           f"WHERE token={token}"
                           )
            # По токену клиент устанавливает свой логин, для запроса сообщений из своей очереди, если токен не валидный,
            # проваливается в ответ 403 и в ссылку на авторизацию
            try:
                my_login = cursor.fetchall()[0][0]
            except IndexError:
                return make_response(["403 Доступ запрещен", 403])
            if my_login:
                # создаем словарик, в который будем помещать имеющиеся в очереди сообщения
                to_receive = {}

                credentials = pika.PlainCredentials('guest', 'guest')
                connection = pika.BlockingConnection(pika.ConnectionParameters(config.rabbit_adress,
                                                                               config.rabbit_port,
                                                                               '/',
                                                                               credentials))
                channel = connection.channel()

                queue = channel.queue_declare(queue=my_login)

                # количество сообщений в очереди
                count = queue.method.message_count

                # пока сообщения в очереди не кончатся,
                # (а их должно быть немного, так как запросы от клиента будут поступать регулярно)
                # вытаскиваем их из очереди, пишем в БД, заносим в наш словарик для клиента
                while count > 0:
                    method_frame, properties, body = channel.basic_get(my_login)
                    data = json.loads(body)

                    login_sender = data['sender']
                    message = data['message']
                    datetime = data['date']

                    if login_sender in to_receive:
                        to_receive[login_sender].update({datetime: message})
                    else:
                        to_receive.update({login_sender: {datetime: message}})

                    con = connections.connection()
                    cur = con.cursor()
                    cur.execute(f"SELECT user_id "
                                "FROM Users "
                                f"WHERE login='{login_sender}';")
                    sender_id = cur.fetchall()[0][0]
                    cur.execute("SELECT user_id "
                                "FROM Users "
                                f"WHERE login='{my_login}';")
                    receiver_id = cur.fetchall()[0][0]
                    cur.execute(f"UPDATE messages SET received ='{True}' "
                                f"WHERE message = '{message}', "
                                f"sender_id = '{sender_id}', "
                                f"receiver_id ='{receiver_id}' "
                                f"send_time = '{datetime}';")
                    con.commit()
                    channel.basic_ack(method_frame.delivery_tag)
                    count -= 1
                channel.close()
                connection.close()

                if len(to_receive):
                    return jsonify(to_receive)
                else:
                    make_response(jsonify(["204 No Content", 204]))
            else:
                return make_response(jsonify(["403 Доступ запрещен", 403]))

        app.run(f"{self.adress}", port=self.port)


StartChat(config.chat_adress, config.chat_port)

