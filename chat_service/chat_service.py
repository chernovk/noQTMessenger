from flask import Flask, request
from flask_restful import Api, Resource
from DB_connections import connections


import pika

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
                sender_login = cursor.fetchall()[0][0]
                if sender_login:
                    # Открываем соединение с очередью (урл прописать который будет на сервере)
                    parameters = pika.URLParameters('localhost')
                    connection = pika.BlockingConnection(parameters)
                    channel = connection.channel()

                    login = request.form['login']

                    # Объявляем очередь, если еще не создана
                    channel.queue_declare(queue=login)

                    package = {
                        'sender': sender_login,
                        'date': request.form['date'],
                        'message': message
                    }

                    channel.basic_publish(exchange='', routing_key=login, body=package)
                    connection.close()
                    return "Сообщение отправлено", 200
                else:
                    return "403 Доступ запрещен", 302, {'location': 'https://localhost:5000/login'}


api.add_resource(SendMessage, '/sendmessage')

if __name__ == '__main__':
    app.run(debug=True)
