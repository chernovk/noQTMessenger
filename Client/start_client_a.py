import sys

from PyQt5.QtWidgets import QMessageBox

sys.path.append('C:/Users/Admin/Desktop/messenger/noQTMessenger')
import requests
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
import datetime
from Client import designTrue
from Client import Sign_In
from Client import Sign_Up
import config

TOKEN = '0'

# Здесь глобально хранится список актуальных собеседников
current_interlocutors = set()

# Здесь глобально хранятся актуальные диалоги
current_dialogues = {}

# Здесь глобально хранится непосредственно выбранный собеседник
current_interlocutor_login = '000'


def verify_data(login, password):
    """
    Функция проверяет валидность введенных данных
    :return: True, если валидность подтверждена, False при ошибке
    """
    if 0 < len(login) <= 20:
        for i in login:
            if not ord('A') <= ord(i) <= ord("z") \
                    and not ord("0") <= ord(i) <= ord("9"):
                return 'incorrect symbols in login'
    else:
        return 'incorrect length of login'
    if 0 < len(password) <= 20:
        for i in password:
            if not ord('A') <= ord(i) <= ord("z") \
                    and not ord("0") <= ord(i) <= ord("9"):
                return 'incorrect symbols in password'
    else:
        return 'incorrect length of password'
    return 'correct form'


class AuthorizeWindow(QtWidgets.QMainWindow, Sign_In.Ui_MainWindow):
    def __init__(self):

        super().__init__()
        self.setupUi(self)

        self.pushButton_2.clicked.connect(self.sign_in)
        self.pushButton_3.clicked.connect(self.sign_up_window)

    def sign_in(self):
        global TOKEN
        login = self.lineEdit.text()
        password = self.lineEdit_2.text()
        if (not login) or (not password):
            QMessageBox.information(self, 'warning', 'fill in all fields')

        elif verify_data(login, password) == 'correct form':
            response = requests.post('http://' + config.auth_address + ":" + str(config.auth_port) + '/get_token/',
                                     data={'login': login, 'password': password})
            if response.status_code == 403:
                QMessageBox.information(self, 'warning', f'Authorisation failed')
            elif response.status_code == 200:
                TOKEN = str(response.json()['token'])
                self.chatWindow = ChatWindow()
                self.chatWindow.show()
                self.close()

        elif verify_data(login, password):
            message = verify_data(login, password)
            QMessageBox.information(self, 'warning', message)

    def sign_up_window(self):
        self.registrationWindow = RegistrationWindow()
        self.registrationWindow.show()
        self.close()


class RegistrationWindow(QtWidgets.QMainWindow, Sign_Up.Ui_MainWindow):
    def __init__(self):

        super().__init__()
        self.setupUi(self)

        self.pushButton_3.clicked.connect(self.sign_up)
        self.pushButton_4.clicked.connect(self.sign_in_window)

    def sign_up(self):
        login = self.lineEdit.text()
        password = self.lineEdit_2.text()
        password_again = self.lineEdit_5.text()

        if (not login) or (not password) or (not password_again):
            QMessageBox.information(self, 'warning', 'fill in all fields')
            return
        elif password != password_again:
            QMessageBox.information(self, 'warning', 'the password repeated incorrectly')
            return

        elif verify_data(login, password) == 'correct form':
            response = requests.post('http://' + config.reg_address + ":" + str(config.reg_port) + '/add_user/',
                                     data={'login': login,
                                           'password': password})

            if response.status_code == 200:
                QMessageBox.information(self, 'Success', 'Now you can Sign In to start chatting')
                self.sign_in_window()
            elif response.status_code == 409:
                QMessageBox.information(self, 'warning', "User with this login already exists")
            else:
                QMessageBox.information(self, 'warning', f"Error {response.status_code}. Try again")

        elif verify_data(login, password):
            message = verify_data(login, password)
            QMessageBox.information(self, 'warning', message)

    def sign_in_window(self):
        self.authorizationWindow = AuthorizeWindow()
        self.authorizationWindow.show()
        self.close()


class ReceiveMessageThread(QThread):
    # Создаем класс потока, который будет получать сообщения для клиента

    # Создаем сигнал, на который будет реагировать gui qt
    about_check_messages = pyqtSignal(dict)

    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def run(self):
        """
        Функция запускает бесконечный цикл в котором раз в 2 секунды посылает запрос на сервер
        :return:
        """
        global TOKEN
        while True:
            response = requests.post('http://' + config.chat_address + ":" + str(config.chat_port) + '/get_messages/',
                                     data={'token': TOKEN})

            try:
                package = response.json()
                if response.status_code == 200 and package:
                    # привязываем событие, которое стриггерит наш сигнал
                    # (получение не пустого пакета сообщений от сервера)
                    self.about_check_messages.emit(package)
            except Exception as e:
                if response.status_code != 204:
                    print(response.status_code, e)
            QThread.msleep(2000)


class ChatWindow(QtWidgets.QMainWindow, designTrue.Ui_MainWindow):
    def __init__(self):

        super().__init__()
        self.setupUi(self)

        # инициализируем поток, запускающийся при открытии окна чата
        self.ReceiveMessage = ReceiveMessageThread(main_window=self)

        # привязываем к сигналу потока функию, которая будет на него реагировать внутри gui qt
        self.ReceiveMessage.about_check_messages.connect(self.on_check_messages)
        # self.ReceiveMessage.start()

    def on_check_messages(self, package):
        """
        Функция по сигналу из потока распаковывает пришедшие с сервера данные, выводит результаты в gui qt
        :param package:
        :return:
        """

        # заполняем пришедшими данными наши кэши собеседников и диалогов
        for interlocutor, message_date in package.items():
            current_interlocutors.add(interlocutor)
            if interlocutor not in current_dialogues:
                current_dialogues[interlocutor] = []
            for date, message in message_date.items():
                string_message = f'{str(date)[:19]} [{interlocutor}]: {message}'
                current_dialogues[interlocutor].append(string_message)

            # обновляем диалоговое окно
            self.ListReceivers.clear()
            self.ListReceivers.addItems(current_interlocutors)
            if current_interlocutor_login != '000':
                conversation = '\n'.join(current_dialogues[current_interlocutor_login])
                self.Dialogue.setPlainText(conversation)

    def receiver_accepted(self):
        """
        Функция привязана к кнопке "утвердить собеседника". Назначает глобально current_interlocutor_login,
        выводит на экран переписку с этим собеседником
        :return:
        """

        global current_interlocutor_login

        current_interlocutor_login = self.ChoseReceiver.text()
        if current_interlocutor_login != '000':
            self.Dialogue.setEnabled(True)
            self.YourMessage.setEnabled(True)
            self.Dialogue.setPlaceholderText('')
            if current_interlocutor_login in current_dialogues:
                conversation = '\n'.join(current_dialogues[current_interlocutor_login])
                self.Dialogue.setPlainText(conversation)
            else:
                self.Dialogue.setPlainText('')

    def send_message(self):
        """
        Функция отправки на сервер сообщения
        :return:
        """
        global TOKEN, current_interlocutor_login
        if self.YourMessage.text():
            message = self.YourMessage.text()
            recipient_login = current_interlocutor_login
            date_time = datetime.datetime.now()
            try:
                response = requests.post('http://' + config.chat_address + ":" + str(config.chat_port) + '/send_message/',
                                         data={'receiver': recipient_login, 'message': message,
                                               'token': TOKEN, 'date': date_time})

                # Отправляем сообщение, если успешно отправилось, заносим в кэши, выводим в gui
                if response.status_code == 200:
                    string_message = f'{str(date_time)[:19]} : {message}'
                    if recipient_login not in current_dialogues:
                        current_dialogues[recipient_login] = [string_message, ]
                        if recipient_login not in current_interlocutors:
                            current_interlocutors.add(recipient_login)
                            self.ListReceivers.clear()
                            self.ListReceivers.addItems(current_interlocutors)
                    else:
                        current_dialogues[recipient_login].append(string_message)
                    conversation = '\n'.join(current_dialogues[current_interlocutor_login])
                    self.Dialogue.setPlainText(conversation)
                    self.YourMessage.setText('')
                # статус 404 придет от сервера, если выберем невалидного собеседника
                elif response.status_code == 404:
                    self.Dialogue.setPlainText('The user you are going to send the message to is not registered')
                # статус 403 придет от сервера, если будут проблемы с токеном
                elif response.status_code == 403:
                    self.Dialogue.setPlainText('Authorization Error')
            except requests.exceptions.ConnectionError:
                self.Dialogue.setEnabled(False)
                self.Dialogue.setPlaceholderText("connection lost")

    def get_history(self):
        """
        запрос истории сообщений с выбранным пользователем
        :return:
        """

        global TOKEN, current_interlocutor_login
        history = []
        current_interlocutor_login = self.ChoseReceiver.text()
        if current_interlocutor_login and current_interlocutor_login != '000':

            date1 = self.dateTimeEdit.text()
            date2 = self.dateTimeEdit_2.text()

            if date1 < date2:
                try:
                    response = requests.post(config.history_address + ":" + str(config.history_port) + '/history/',
                                             data={'interlocutor_login': current_interlocutor_login,
                                                   'token': TOKEN, 'date1': date1, 'date2': date2})
                    if response.status_code == 200:
                        package = response.json()
                        for message in package:
                            if message[0] == current_interlocutor_login:
                                string_message = f'{message[3]} [{message[0]}]: {message[2]}'
                            else:
                                string_message = f'{message[3]} : {message[2]}'
                            history.append(string_message)

                        history_text = '\n'.join(history)
                        self.Dialogue.setPlainText(history_text)

                    # статус 404 придет от сервера, если выберем невалидного собеседника
                    elif response.status_code == 404:
                        self.Dialogue.setPlainText('The user you are going get history of '
                                                   'conversation with is not registered')
                    # статус 403 придет от сервера, если будут проблемы с токеном
                    elif response.status_code == 403:
                        self.Dialogue.setPlainText('Authorization Error')
                except requests.exceptions.ConnectionError:
                    self.Dialogue.setEnabled(False)
                    self.Dialogue.setPlaceholderText("connection lost")


def main():
    app = QtWidgets.QApplication(sys.argv)
    # window = ChatWindow()
    window = AuthorizeWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
