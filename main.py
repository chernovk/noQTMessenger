from flask import Flask, request, make_response, jsonify
from reg.registration import AddUser
from authorize.auth import GetToken

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
        return make_response("Пользователь добавлен в базу!", 200)
    else:
        return make_response("Ошибка добавления!", 400)


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
        return make_response(jsonify([token]), 200)
    else:
        return make_response("Ошибка авторизации!", 403)


if __name__ == "__main__":
    app.run("127.0.0.1", port=8888)
