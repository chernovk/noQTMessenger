# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(542, 464)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")
        self.SenMessageButton = QtWidgets.QPushButton(self.centralwidget)
        self.SenMessageButton.setObjectName("SenMessageButton")
        self.SenMessageButton.clicked.connect(self.send_message)
        self.gridLayout.addWidget(self.SenMessageButton, 4, 0, 1, 2)
        self.YourMessage = QtWidgets.QLineEdit(self.centralwidget)
        self.YourMessage.setEnabled(False)
        self.YourMessage.setObjectName("YourMessage")
        self.gridLayout.addWidget(self.YourMessage, 3, 0, 1, 2)
        self.ChoseReceiver = QtWidgets.QLineEdit(self.centralwidget)
        self.ChoseReceiver.setText("")
        self.ChoseReceiver.setObjectName("ChoseReceiver")
        self.gridLayout.addWidget(self.ChoseReceiver, 0, 1, 1, 1)
        self.ListReceivers = QtWidgets.QListWidget(self.centralwidget)
        self.ListReceivers.setEnabled(True)
        self.ListReceivers.itemClicked.connect(self.receiver_selected)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ListReceivers.sizePolicy().hasHeightForWidth())
        self.ListReceivers.setSizePolicy(sizePolicy)
        self.ListReceivers.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.ListReceivers.setObjectName("ListReceivers")
        self.gridLayout.addWidget(self.ListReceivers, 2, 1, 1, 1)
        self.Dialogue = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.Dialogue.setEnabled(False)
        self.Dialogue.setObjectName("Dialogue")
        self.Dialogue.setPlaceholderText("Chose or enter the interlocutor's login to start chatting")
        self.gridLayout.addWidget(self.Dialogue, 0, 0, 3, 1)
        self.AcceptReceiverButton = QtWidgets.QPushButton(self.centralwidget)
        self.AcceptReceiverButton.setObjectName("AcceptReceierButton")
        self.AcceptReceiverButton.clicked.connect(self.receiver_accepted)
        self.gridLayout.addWidget(self.AcceptReceiverButton, 1, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def receiver_selected(self, item):
        self.ChoseReceiver.setText(item.text())

    def receiver_accepted(self):
        pass

    def send_message(self):
        pass

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.SenMessageButton.setText(_translate("MainWindow", "Send Message"))
        self.AcceptReceiverButton.setText(_translate("MainWindow", "Accept Recipient"))
