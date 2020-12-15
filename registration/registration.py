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
        cursor = con.cursor()
        try:
            cursor.execute(
                f"SELECT * "
                f"FROM users "
                f"WHERE login={self.login};"
            )
            result = cursor.fetchall()
            if len(result):
                return 'User with this login already exists'
            else:
                cursor.execute(
                    f"INSERT INTO messenger.users (login, password, token_number) \
                    VALUES ('{self.login}', '{self.password}', '{self.token}');"
                )
                con.commit()
                return 'Successfully registered'
        except Exception as e:
            return f'{e}'


