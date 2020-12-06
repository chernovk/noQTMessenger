from DB_connections import connections
import random


class AddUser:
    def __init__(self, login: str, password: str, name: str):
        self.login = login
        self.password = password
        self.name = name
        self.token = random.randint(1000000, 9999999)

    def create_user(self):
        """
        Метод создает подключение к БД, запускает метод верификации данных пользователя,
        если получает в ответ True - пытается записать данные пользователя в БД. При ошибке
        выводит сообщение об ошибке.
        :return: True, если добавление пользователя в БД прошло успешно.
                 False, если добавление не удалось
        """
        con = connections.connection()
        if self.verify_data():
            cursor = con.cursor()
            try:
                cursor.execute(
                    f"INSERT INTO messenger.users (login, password, name, token_number) \
                    VALUES ('{self.login}', '{self.password}', '{self.name}', '{self.token}');"
                )
                con.commit()
                print("Пользователь успешно добавлен!")
                return True
            except Exception:
                print("Не удалось зарегестрировать нового пользователя!")
        return False

    def verify_data(self):
        """
        Метод проверяет валидность введенных данных по длине
        :return: True, если валидность подтверждена
        """
        if 0 < len(self.login) <= 20 and \
                0 < len(self.password) <= 20 and \
                0 < len(self.name) <= 20:
            return True
