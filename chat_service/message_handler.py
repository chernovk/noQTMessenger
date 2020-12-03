import json
import logging

from flask import Flask, jsonify, request, make_response
from flask_restful import Api, Resource
import sqlite3

import pika

app = Flask(__name__)
api = Api(app)


class ReceiveMessage(Resource):
    def post(self):
        """
        Выдаем клиенту сообщение по его токену из очеереди сообщений

        :return:
        """
        token = request.form['token']
        conn = sqlite3.connect("tokens")
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Users.login "
                           "FROM Tokens "
                           "INNER JOIN Users "
                           "ON Users.user_id = Tokens.user_id "
                           f"WHERE token={token}"
                           )
            try:
                my_login = cursor.fetchall()[0][0]
            except IndexError:
                return "403 Доступ запрещен", 403
            if my_login:

                to_receive = {}

                credentials = pika.PlainCredentials('guest', 'guest')
                connection = pika.BlockingConnection(pika.ConnectionParameters('localhost',
                                                                               5672,
                                                                               '/',
                                                                               credentials))
                channel = connection.channel()

                queue = channel.queue_declare(queue=my_login)

                method, properties, body = channel.basic_get(my_login)
                print(body)
                if method:
                    count = queue.method.message_count
                    while count > 0:
                        data = json.loads(body)

                        login_sender = data['sender']
                        message = data['message']
                        datetime = data['date']

                        if login_sender in to_receive:
                            to_receive[login_sender].update({datetime: message})
                        else:
                            to_receive.update({login_sender: {datetime: message}})

                        con = sqlite3.connect("tokens")
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
                        count -= 1

                    return jsonify(to_receive)
                return make_response('No content', 204)

            else:
                return make_response("403 Доступ запрещен", 403)


api.add_resource(ReceiveMessage, '/receivemessage')

if __name__ == '__main__':
    app.run(debug=True)