from flask import Flask, request, make_response, jsonify
from authorisation.authorisation import GetToken
import config


class StartAuth:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        app = Flask(__name__)

        @app.route("/get_token/", methods=["POST"])
        def get_token():
            """
            Функция получает GET запрос с атрибутами login и password от пользовательского
            сервиса, запрашивает по данным атрибутам токен для данного пользователя у класса
            GetToken.
            :return: token и код 200 при успешном получении токена
                     код 403 и сообщение об ошибке при отказе в получении токена
            """
            login = request.form["login"]
            password = request.form["password"]
            new_token = GetToken(login, password)
            token = new_token.get_token()
            if token is not None:
                return jsonify({'token': token})
            else:
                return make_response("Authorisation failed", 403)

        app.run(self.address, self.port, debug=True)


StartAuth(config.auth_address, config.auth_port)
