# This Python file uses the following encoding: utf-8
import sys
from PyQt6 import QtWidgets, uic

def test():

    window.textEdit.append("Hello!")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = uic.loadUi("mainwindow.ui")
    window.pushButton.clicked.connect(test)
    window.show()
    app.exec()
