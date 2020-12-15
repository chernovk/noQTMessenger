from DB_connections import connections
import random


class GetToken:
    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password

    def get_token(self):
        """
        Метод по полученныму логину получает из БД данные пользователя, проверяет
        наличие в базе логина и соответствие пароля логину и пытается записать в БД
        новый токен для данного пользователя.
        :return: token, при успешном внесении токена в базу
                 False при невозможности внесения токена в базу по полученным параметрам
        """
        con = connections.connection()
        with con:
            cursor = con.cursor()
            cursor.execute(
                f"SELECT login, password, user_id FROM messenger.users \
                           WHERE login =?;", self.login)
            result = cursor.fetchall()
            if result and result[0][1] == self.password:
                token = random.randint(1000000, 9999999)
                try:
                    cursor.execute(
                        f"UPDATE messenger.users SET token_number = '{token}' "
                        f"WHERE (user_id = '{result[0][2]}');"
                    )
                    con.commit()
                    return token
                except Exception as e:
                    print(e)

