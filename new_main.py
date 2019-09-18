import sys
from main_window_structure_generator import Ui_MainWindow
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class IntegratedWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(IntegratedWindow, self).__init__()
        self.setupUi(self)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = IntegratedWindow()
    win.show()
    sys.exit(app.exec_())
