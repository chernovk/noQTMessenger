import datetime

from flask import Flask, request, make_response, jsonify
from DB_connections import connections
import config


class Verification:
    def __init__(self, token, receiver):
        self.token = token
        self.receiver = receiver

    def verify_data(self):
        con = connections.connection()
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
                login = cursor.fetchall()[0][0]
                if not login:
                    return 'authorization error'
            except IndexError:
                return 'authorization error'

            return login


class StartHistory:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        app = Flask(__name__)

        @app.route("/history/", methods=["POST"])
        def get_history():
            """
            Функция принимает данные из пост запроса от клиента в виде его токена, логина интересующего его собеседника
            и двух дат, ограничивающих интересующий его период времени переписки, по этим данным из БД извлекается
            набор сообщений для отправки на клиент пользователю
            :return: http response (код ответа с сообщением о том успешно ли доставлено сообщение)
            в случае наличия запрашиваемых сообщений в БД, возвращаются данные в виде списка history_pack,
            состоящего из сообщений, представленных, в свою очередь, в виде списков вида
             [логин_запрашивающего, логин_собеседника, сообщение, дата-время].
            Список history_pack сериализуется в JSON
            """
            # сюда занесем выбранные из базы сообщения
            history_pack = []

            token = request.form["token"]
            interlocutor_login = request.form['interlocutor_login']
            date1 = request.form['date1']
            date2 = request.form['date2']
            verify_message = Verification(token, interlocutor_login)
            if verify_message.verify_data() == 'authorization error':
                return make_response("403 Forbidden", 403)
            elif verify_message.verify_data() == 'receiver error':
                return make_response("404 Receiver Not Found", 404)
            elif verify_message.verify_data():
                requester_login = verify_message.verify_data()
                con = connections.connection()

                # Находим user_id, соответствующие логинам
                with con:
                    cur = con.cursor()
                    cur.execute(f"SELECT user_id "
                                "FROM users "
                                f"WHERE login=?;", requester_login)
                    requester_id = cur.fetchall()[0][0]
                    cur.execute(f"SELECT user_id "
                                "FROM users "
                                f"WHERE login=?;", interlocutor_login)
                    interlocutor_id = cur.fetchall()[0][0]

                date1_format = datetime.datetime.strptime(date1, '%d.%m.%Y %H:%M')
                date2_format = datetime.datetime.strptime(date2, '%d.%m.%Y %H:%M')
                con = connections.connection()
                with con:
                    cursor = con.cursor()
                    cursor.execute("SELECT * "
                                   "FROM messages "
                                   f"WHERE sender_id IN (?, ?)"
                                   f"AND receiver_id IN (?, ?)"
                                   f"AND send_time >= ?"
                                   f"AND send_time <= ?;",
                                   requester_id, interlocutor_id,
                                   requester_id, interlocutor_id, f'{date1_format}', f'{date2_format}')

                    try:
                        messages = cursor.fetchall()
                        if messages:
                            for message in messages:
                                if message[0] != message[1]:
                                    transaction = []
                                    if message[0] == requester_id:
                                        transaction.append(requester_login)
                                    elif message[0] == interlocutor_id:
                                        transaction.append(interlocutor_login)
                                    if message[1] == requester_id:
                                        transaction.append(requester_login)
                                    elif message[1] == interlocutor_id:
                                        transaction.append(interlocutor_login)
                                    transaction.append(message[2])
                                    transaction.append(str(message[3]))
                                    history_pack.append(transaction)
                            return jsonify(history_pack)
                        else:
                            return make_response("204 No Content", 204)
                    except IndexError:
                        return make_response("204 No Content", 204)

        app.run(debug=True)


StartHistory(config.history_address, config.history_port)
