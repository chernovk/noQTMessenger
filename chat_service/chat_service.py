import json

from flask import Flask, request
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
                    return "403 Доступ запрещен", 302, {'location': 'https://localhost:5000/login'}






api.add_resource(SendMessage, '/sendmessage')

if __name__ == '__main__':
    app.run(debug=True)
