import json
import sys, os
sys.path.append('C:/Users/Admin/Desktop/messenger/noQTMessenger')
from flask import Flask, request, jsonify, make_response
import pika
import config


from DB_connections import connections


class Verification:
    def __init__(self, message, token, receiver):
        self.message = message
        self.token = token
        self.receiver = receiver

    def verify_data(self):
        con = connections.connection()
        if self.message:
            with con:
                try:
                    cursor = con.cursor()
                    cursor.execute(f"SELECT login "
                                   f"FROM users "
                                   f"WHERE login=?;", self.receiver)
                    result = cursor.fetchall()[0][0]
                    if not result:
                        return 'receiver error'
                except IndexError:
                    return 'receiver error'
                try:
                    cursor = con.cursor()
                    cursor.execute(f"SELECT login "
                                   f"FROM users "
                                   f"WHERE token_number=?;", self.token)
                    sender_login = cursor.fetchall()[0][0]
                    if not sender_login:
                        return 'authorization error'
                except IndexError:
                    return 'authorization error'

            return sender_login


class StartChat:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        app = Flask(__name__)

        @app.route("/send_message/", methods=["POST"])
        def send_message():
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
            date = request.form['date']

            verify_message = Verification(message, token, receiver)
            if verify_message.verify_data() == 'authorization error':
                return make_response("403 Forbidden", 403)
            elif verify_message.verify_data() == 'receiver error':
                return make_response("404 Receiver Not Found", 404)
            elif verify_message.verify_data():
                # Если проверка на наличие сообщения, на правильность логина получателя
                # и на валидность токена отправителя проходит, валидатор возвращает
                # установленный по токену логин отправителя, который идет в package
                sender_login = verify_message.verify_data()
                credentials = pika.PlainCredentials('www', 'pass')
                connection = pika.BlockingConnection(pika.ConnectionParameters(config.rabbit_address,
                                                                               config.rabbit_port,
                                                                               '/',
                                                                               credentials))
                channel = connection.channel()

                channel.queue_declare(queue=receiver)
                package = json.dumps({
                    'sender': sender_login,
                    'date': date,
                    'message': message
                })
                channel.basic_publish(exchange='', routing_key=receiver, body=package)
                connection.close()
                return make_response("Successfully sent", 200)

        @app.route("/get_messages/", methods=["POST"])
        def get_messages():
            """
            Выдаем клиенту сообщение по его токену из очереди сообщений
            По моей идее, клиент регулярно посылает POST запрос на сервер, запрашивая новые сообщения для него.
            в этом запросе он передает свой токен (поэтому пост запрос, т.к. токен не должен быть в урле)
            :return:
            """
            # data = request.get_json()
            # token = data["token"]
            token = request.form["token"]
            con = connections.connection()
            with con:
                cursor = con.cursor()
                cursor.execute("SELECT login "
                               "FROM users "
                               f"WHERE token_number=?", token)
                # По токену клиент устанавливает свой логин, для запроса сообщений из своей очереди, если токен не
                # валидный, проваливается в ответ 403 и в ссылку на авторизацию
                try:
                    my_login = cursor.fetchall()[0][0]
                except IndexError:
                    return make_response("403 Forbidden", 403)
            if my_login:
                # создаем словарик, в который будем помещать имеющиеся в очереди сообщения
                to_receive = {}

                credentials = pika.PlainCredentials('www', 'pass')
                connection = pika.BlockingConnection(pika.ConnectionParameters(config.rabbit_address,
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
                    with con:
                        cur = con.cursor()
                        cur.execute(f"SELECT user_id "
                                    "FROM users "
                                    f"WHERE login=?;", login_sender)
                        sender_id = cur.fetchall()[0][0]
                        cur.execute("SELECT user_id "
                                    "FROM users "
                                    f"WHERE login=?;", my_login)
                        receiver_id = cur.fetchall()[0][0]
                        cur.execute("INSERT INTO messages(message, sender_id, receiver_id, send_time) "
                                    f"VALUES(?, ?, ?, ?)", (message, sender_id, receiver_id, datetime))
                        con.commit()
                    channel.basic_ack(method_frame.delivery_tag)
                    count -= 1
                channel.close()
                connection.close()

                if len(to_receive):
                    return jsonify(to_receive)
                else:
                    return make_response("204 No Content", 204)
            else:
                return make_response("403 Authorization error", 403)

        app.run(debug=True)


StartChat(config.chat_address, config.chat_port)
