from DB_connections import connections


class AddUser:
    def __init__(self, login: str, password: str, name: str, email=None):
        self.login = login
        self.password = password
        self.name = name
        self.email = email

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
            with con:
                cursor = con.cursor()
                try:
                    cursor.execute(
                        f"INSERT INTO `messenger`.`users` (`login`, `password`, `name`, `email`) \
                                   VALUES ('{self.login}', '{self.password}', '{self.name}, {self.email}');"
                    )
                    con.commit()
                    print("Пользователь успешно добавлен!")
                    return True
                except:
                    print("Не удалось зарегестрировать нового пользователя!")
        return False

    def verify_data(self):
        """
        Метод проверяет валидность введенных данных по длине
        :return: True, если валидность подтверждена
        """
        if len(self.login) <= 20 and len(self.password) <= 20 and len(self.name) <= 20:
            return True
