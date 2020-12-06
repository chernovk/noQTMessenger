from flask import Flask, request, make_response, jsonify
from authorize.auth import GetToken
import config


class StartAuth:
    def __init__(self, adress, port):
        self.adress = adress
        self.port = port
        app = Flask(__name__)

        @app.route("/get_token/", methods=["GET"])
        def get_token():
            """
            Функция получает GET запрос с атрибутами login и password от пользовательского
            сервиса, запрашивает по данным атрибутам токен для данного пользователя у класса
            GetToken.
            :return: token и код 200 при успешном получении токена
                     код 403 и сообщение об ошибке при отказе в получении токена
            """
            login = request.args.get("login")
            password = request.args.get("password")
            new_token = GetToken(login, password)
            token = new_token.get_token()
            if token:
                return make_response(jsonify([token, 200]))
            else:
                return make_response(jsonify(["Ошибка авторизации!", 403]))

        app.run(f"{self.adress}", port=self.port)


StartAuth(config.auth_adress, config.auth_port)
