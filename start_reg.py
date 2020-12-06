from flask import Flask, request, make_response, jsonify
from reg.registration import AddUser
import config


class StartReg:
    def __init__(self, adress, port):
        self.adress = adress
        self.port = port
        app = Flask(__name__)

        @app.route("/add_user/", methods=["GET"])
        def add_user():
            """
            Функция добавления нового пользователя. Принимает GET запрос в виде url с
            обязательными параметрами login, password, name от клиента и пытается через класс
            AddUser добавить пользователя в базу.
            :return: Код 200 и соответствующее сообщение, если попытка удачна, иначе код 400
            """
            login = request.args.get("login")
            password = request.args.get("password")
            user = AddUser(login, password)
            if user.create_user():
                return make_response(jsonify(["New user successfully added", 200]))
            else:
                return make_response(jsonify(["Error!", 400]))

        app.run(f"{self.adress}", port=self.port)


StartReg(config.reg_adress, config.reg_port)
