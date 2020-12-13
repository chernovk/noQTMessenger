import sys
sys.path.append('C:/Users/Admin/Desktop/messenger/noQTMessenger')
import requests
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread, pyqtSignal
import datetime
from Client import designTrue

BASE = 'http://127.0.0.1:5000/'
token = '111'

# Здесь глобально хранится список актуальных собеседников
current_interlocutors = set()

# Здесь глобально хранятся актуальные диалоги
current_dialogues = {}

# Здесь глобально хранится непосредственно выбранный собеседник
current_interlocutor_login = '000'


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
        while True:
            response = requests.post(BASE + 'get_messages/', data={'token': token})
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
        global token, current_interlocutor_login
        if self.YourMessage.text():
            message = self.YourMessage.text()
            recipient_login = current_interlocutor_login
            date_time = datetime.datetime.now()
            try:
                response = requests.post(BASE + 'send_message/', data={'receiver': recipient_login, 'message': message,
                                                                       'token': token, 'date': date_time})
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

        global token, current_interlocutor_login
        history = []
        current_interlocutor_login = self.ChoseReceiver.text()
        if current_interlocutor_login and current_interlocutor_login != '000':

            date1 = self.dateTimeEdit.text()
            date2 = self.dateTimeEdit_2.text()

            if date1 < date2:
                try:
                    response = requests.post(BASE + 'history/', data={'interlocutor_login': current_interlocutor_login,
                                                                      'token': token, 'date1': date1, 'date2': date2})
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
    window = ChatWindow()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
