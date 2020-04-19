from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys


class About_page(QMainWindow):
    """This class defines about page.
    """
    def __init__(self):
        super(About_page, self).__init__()

        self.__textbox = QTextEdit(self)
        self.setWindowTitle("About")
        self.setCentralWidget(self.__textbox)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        self.__initAbout()

    def __initAbout(self):
        self.__textbox.setReadOnly(True)

        self.__setPageText()


    def __setPageText(self):
        self.filename = 'userInteface/about_page_content.txt'
        if self.filename:
            with open(self.filename, "rt") as file:
                self.__textbox.setText(file.read())





