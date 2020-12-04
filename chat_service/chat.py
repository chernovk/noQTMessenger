import json

from flask import Flask, request, jsonify, make_response
from flask_restful import Api, Resource
import pika

from DB_connections import connections

app = Flask(__name__)
api = Api(app)


class SendMessage(Resource):
    def post(self):
        """
        Принимаем от клиента сообщение, его токен, логин адресата и дату/время отправки.
        Токен сверяем с БД. Если корректный:
        Подключаемся к очереди RabbitMQ, кладем в очередь с названием логина адресата сообщение
        и дату/время его отправки в JSON формате.

        :return:
        """
        message = request.form['message']
        if message:
            token = request.form['token']
            con = connections.connection()
            with con:
                cursor = con.cursor()
                cursor.execute("SELECT Users.login "
                               "FROM Tokens "
                               "INNER JOIN Users "
                               "ON Users.user_id = Tokens.user_id "
                               f"WHERE token={token}"
                               )
                try:
                    sender_login = cursor.fetchall()[0][0]
                except IndexError:
                    return "403 Доступ запрещен", 403
                if sender_login:
                    # Открываем соединение с очередью (урл прописать который будет на сервере)
                    credentials = pika.PlainCredentials('guest', 'guest')
                    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',
                                                                                   5672,
                                                                                   '/',
                                                                                   credentials))
                    channel = connection.channel()

                    login = request.form['login']

                    # Объявляем очередь, если еще не создана
                    channel.queue_declare(queue=login)

                    package = json.dumps({
                        'sender': sender_login,
                        'date': request.form['date'],
                        'message': message
                    })

                    channel.basic_publish(exchange='', routing_key=login, body=package)
                    connection.close()
                    return "Сообщение отправлено", 200
                else:
                    # урл прописать который будет на сервере
                    # TODO
                    return "403 Доступ запрещен", 302, {'location': 'https://localhost:5000/login'}


class ReceiveMessage(Resource):
    def post(self):
        """
        Выдаем клиенту сообщение по его токену из очеереди сообщений
        По моей идее, клиент регулярно посылает POST запрос на сервер, запрашивая новые сообщения для него.
        в этом запросе он передает свой токен (поэтому пост запрос, т.к. токен не должен быть в урле)

        :return:
        """
        token = request.form['token']
        con = connections.connection()
        with con:
            cursor = con.cursor()
            cursor.execute("SELECT Users.login "
                           "FROM Tokens "
                           "INNER JOIN Users "
                           "ON Users.user_id = Tokens.user_id "
                           f"WHERE token={token}"
                           )
            # По токену клиент устанавливает свой логин, для запроса сообщений из своей очереди, если токен не валидный,
            # проваливается в ответ 403 и в ссылку на авторизацию
            try:
                my_login = cursor.fetchall()[0][0]
            except IndexError:
                # TODO
                return "403 Доступ запрещен", 403
            if my_login:

                # создаем словарик, в который будем помещать имеющиеся в очереди сообщения
                to_receive = {}

                credentials = pika.PlainCredentials('guest', 'guest')
                connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',
                                                                               5672,
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
                                    "FROM Users "
                                    f"WHERE login=?", [login_sender])
                        sender_id = cur.fetchall()[0][0]
                        cur.execute("SELECT user_id "
                                    "FROM Users "
                                    f"WHERE login=?", [my_login])
                        receiver_id = cur.fetchall()[0][0]
                        cur.execute("INSERT INTO Messages(sender_id, receiver_id, date, message) "
                                    "VALUES(?, ?, ?, ?)", [sender_id, receiver_id, datetime, message])
                        con.commit()
                    channel.basic_ack(method_frame.delivery_tag)
                    count -= 1
                channel.close()
                connection.close()

                if len(to_receive):
                    return jsonify(to_receive)
                else:
                    make_response("204 No Content", 204)
            else:
                # TODO
                return make_response("403 Доступ запрещен", 403)


api.add_resource(SendMessage, '/sendmessage')

api.add_resource(ReceiveMessage, '/receivemessage')

if __name__ == '__main__':
    app.run(debug=True)


