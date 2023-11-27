# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'startWarning.ui'
##
## Created by: Qt User Interface Compiler version 6.5.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QPushButton,
    QSizePolicy, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(400, 300)
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(20, 100, 361, 131))
        font = QFont()
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setWordWrap(True)
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(150, 10, 91, 91))
        self.label_2.setTextFormat(Qt.RichText)
        self.label_2.setPixmap(QPixmap(u"assets/warning.png"))
        self.label_2.setScaledContents(True)
        self.pushButton = QPushButton(Dialog)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setGeometry(QRect(140, 230, 100, 32))
        self.pushButton.setAutoFillBackground(False)

        self.retranslateUi(Dialog)
        self.pushButton.released.connect(Dialog.accept)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"WARNING!", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"This application is only to be used by AEM Personnel! \n"
"By clicking OK, you acknowledge you have permission to use this application.", None))
        self.label_2.setText("")
        self.pushButton.setText(QCoreApplication.translate("Dialog", u"Accept", None))
    # retranslateUi

