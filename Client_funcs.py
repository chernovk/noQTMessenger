import requests


def register(ip: str, port: int, login: str, password: str):

    # Посылаем запрос на сервер в каком-нибудь таком виде и получаем ответ
    response = requests.request(
        "POST", url=f"https://{ip}:{port}/API/reg?login={login}&pass={password}"
    )

    # Достаем из ответа ответ и возвращаем его
    otvet = response.text
    return otvet


def authorise(ip: str, port: int, login: str, password: str) -> str:

    # Посылаем запрос на сервер в каком-нибудь таком виде и получаем ответ
    response = requests.request(
        "POST", url=f"https://{ip}:{port}/API/auth?login={login}&pass={password}"
    )

    # Достаем из ответа токен и возвращаем его
    token = response.text
    return token


def send_message(ip: str, port: int, token: str, message: str, adresat: str):

    # Посылаем запрос на сервер в каком-нибудь таком виде и получаем ответ
    response = requests.request(
        "POST",
        url=f"https://{ip}:{port}/API/send?token={token}&message={message}&adresat={adresat}",
    )

    # Достаем из ответа ответ и возвращаем его
    otvet = response.text
    return otvet


def get_history(ip: str, port: int, token: str, adresat: str):

    # Посылаем запрос на сервер в каком-нибудь таком виде и получаем ответ
    response = requests.request(
        "POST",
        url=f"https://{ip}:{port}/API/get_history?token={token}&adresat={adresat}",
    )

    # Достаем из ответа ответ и возвращаем его
    otvet = response.text
    return otvet
