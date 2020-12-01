import sys

from PyQt5 import uic, QtWidgets


class MainWindow(QtWidgets.QMainWindow, uic.loadUiType("main_window.ui")[0]):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    a = MainWindow()
    a.show()

    sys.exit(app.exec_())
