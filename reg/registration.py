from DB_connections import connections
import random


class AddUser:
    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password
        self.token = random.randint(1000000, 9999999)

    def __delete_user__(self):
        """
        Метод удаляет пользователя из БД
        :return: True, если удаление прошло успешно, False, если возникла ошибка
        """
        con = connections.connection()
        if self.verify_data():
            cursor = con.cursor()
            try:
                cursor.execute(
                    f"DELETE FROM messenger.users WHERE (login = '{self.login}');"
                )
                con.commit()
                return True
            except Exception as e:
                print(e)
        return False

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
                    f"INSERT INTO messenger.users (login, password, token_number) \
                    VALUES ('{self.login}', '{self.password}', '{self.token}');"
                )
                con.commit()
                return True
            except Exception as e:
                print(e)
        return False

    def verify_data(self):
        """
        Метод проверяет валидность введенных данных
        :return: True, если валидность подтверждена, False при ошибке
        """
        if 0 < len(self.login) <= 20:
            for i in self.login:
                if not ord('A') <= ord(i) <= ord("z") \
                        and not ord("0") <= ord(i) <= ord("9"):
                    return False
        else:
            return False
        if 0 < len(self.password) <= 20:
            for i in self.password:
                if not ord('A') <= ord(i) <= ord("z") \
                        and not ord("0") <= ord(i) <= ord("9"):
                    return False
        else:
            return False
        return True
