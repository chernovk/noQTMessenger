from reg.registration import AddUser


# Получает от сервиса клиента POST запрос /add_user/?login="...";password="...";name="..."
if __name__ == '__main__':
    user = AddUser("Ustas", "111111", "Ustas")
    user.create_user()
