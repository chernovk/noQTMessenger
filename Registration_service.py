from flask import Flask, request, make_response, jsonify
from registration.registration import AddUser
import config


class StartReg:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        app = Flask(__name__)

        @app.route("/add_user/", methods=["POST"])
        def add_user():
            """
            Функция добавления нового пользователя. Принимает POST запрос с данными:
             login, password, от клиента и пытается через класс
            AddUser добавить пользователя в базу.
            :return: Код 200 и соответствующее сообщение, если попытка удачна, иначе код 400
            """
            login = request.form["login"]
            password = request.form["password"]
            user = AddUser(login, password)
            if user.create_user() == 'Successfully registered':
                return make_response("New user successfully added", 200)
            elif user.create_user() == 'User with this login already exists':
                return make_response("User with this login already exists", 409)
            else:
                msg = user.create_user()
                print(msg)
                return make_response('error', 500)

        app.run(self.address, self.port, debug=True)


StartReg(config.reg_address, config.reg_port)
