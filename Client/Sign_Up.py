# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Sign_Up.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(430, 290)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridFrame = QtWidgets.QFrame(self.centralwidget)
        self.gridFrame.setEnabled(True)
        self.gridFrame.setGeometry(QtCore.QRect(80, 90, 291, 74))
        self.gridFrame.setMinimumSize(QtCore.QSize(0, 74))
        self.gridFrame.setAcceptDrops(False)
        self.gridFrame.setInputMethodHints(QtCore.Qt.ImhNone)
        self.gridFrame.setObjectName("gridFrame")
        self.gridLayout = QtWidgets.QGridLayout(self.gridFrame)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.gridFrame)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.gridFrame)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.lineEdit = QtWidgets.QLineEdit(self.gridFrame)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout.addWidget(self.lineEdit, 0, 1, 1, 1)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.gridFrame)
        self.lineEdit_2.setFrame(True)
        self.lineEdit_2.setDragEnabled(False)
        self.lineEdit_2.setClearButtonEnabled(False)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.gridLayout.addWidget(self.lineEdit_2, 1, 1, 1, 1)
        self.lineEdit_5 = QtWidgets.QLineEdit(self.gridFrame)
        self.lineEdit_5.setFrame(True)
        self.lineEdit_5.setDragEnabled(False)
        self.lineEdit_5.setClearButtonEnabled(False)
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.gridLayout.addWidget(self.lineEdit_5, 2, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.gridFrame)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(120, 180, 176, 25))
        self.pushButton_3.setStyleSheet("font: 11pt \"Ubuntu\";")
        self.pushButton_3.setObjectName("pushButton_3")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(160, 30, 101, 41))
        font = QtGui.QFont()
        font.setFamily("Ubuntu Condensed")
        font.setPointSize(20)
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(9)
        self.label_3.setFont(font)
        self.label_3.setStyleSheet("font: 75 italic 20pt \"Ubuntu Condensed\";\n"
"")
        self.label_3.setObjectName("label_3")
        self.label_8 = QtWidgets.QLabel(self.centralwidget)
        self.label_8.setGeometry(QtCore.QRect(180, 250, 61, 20))
        self.label_8.setObjectName("label_8")
        self.pushButton_4 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_4.setGeometry(QtCore.QRect(120, 210, 176, 25))
        self.pushButton_4.setStyleSheet("font: 11pt \"Ubuntu\";")
        self.pushButton_4.setObjectName("pushButton_4")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Registration"))
        self.label.setText(_translate("MainWindow", "login"))
        self.label_2.setText(_translate("MainWindow", "password"))
        self.label_4.setText(_translate("MainWindow", "password again"))
        self.pushButton_3.setText(_translate("MainWindow", "Sign Up"))
        self.label_3.setText(_translate("MainWindow", "Sign Up"))
        self.pushButton_4.setText(_translate("MainWindow", "Sign In"))
