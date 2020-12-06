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
            name = request.args.get("name")
            email = request.args.get("email")
            user = AddUser(login, password, name, email)
            if user.create_user():
                return make_response(jsonify(["Пользователь добавлен в базу!", 200]))
            else:
                return make_response(jsonify(["Ошибка добавления!", 400]))

        app.run(f"{self.adress}", port=self.port)


StartReg(config.reg_adress, config.reg_port)
