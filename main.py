from flask import Flask, request, make_response
from reg.registration import AddUser


app = Flask(__name__)


@app.route('/add_user/', methods=['GET'])
def add_user():
    """
    Функция добавления нового пользователя. Принимает GET запрос в виде url с
    обязательными параметрами login, password, name и пытается через класс AddUser
    добавить пользователя в базу.
    :return: Код 200 и соответствующее сообщение, если попытка удачна, иначе код 400
    """
    login = request.args.get("login")
    password = request.args.get("password")
    name = request.args.get("name")
    user = AddUser(login, password, name)
    if user.create_user():
        return make_response("Пользователь добавлен в базу!", 200)
    else:
        return make_response("Ошибка добавления!", 400)


if __name__ == '__main__':
    app.run("127.0.0.1", port=8888)
