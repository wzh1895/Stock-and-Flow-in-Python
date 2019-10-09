import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from StockAndFlowInPython.sfd_canvas.interactive_sfd_ui import Ui_widget_interactive_sfd


class InteractiveSFD(QGraphicsScene):
    def __init__(self):
        super(InteractiveSFD, self).__init__()

        self.n = 0

    def mousePressEvent(self, e):
        print(e)
        print('Press position:', e.pos().x(), e.pos().y())
        self.add_stock(e.pos().x(), e.pos().y())

    def mouseDoubleClickEvent(self, e):
        print(e)
        print('Double Click position:', e.pos().x(), e.pos().y())

    def add_stock(self, x, y, w=50, h=30):
        qrect = QRectF(self.n*20, self.n*20, w, h)
        self.addItem(QGraphicsRectItem(qrect))
        self.n+=1


class WangSim(QWidget, Ui_widget_interactive_sfd):
    def __init__(self):
        super(WangSim, self).__init__()
        self.setupUi(self)
        self.pushButton_add_stock.setCheckable(True)
        self.pushButton_add_flow.setCheckable(True)
        self.pushButton_add_aux.setCheckable(True)
        self.pushButton_add_connector.setCheckable(True)

        self.pushButton_add_stock.clicked.connect(self.on_pushbutton_add_stock_pushed)
        self.pushButton_add_flow.clicked.connect(self.on_pushbutton_add_flow_pushed)
        self.pushButton_add_aux.clicked.connect(self.on_pushbutton_add_aux_pushed)
        self.pushButton_add_connector.clicked.connect(self.on_pushbutton_add_connector_pushed)

        self.interactive_sfd = InteractiveSFD()
        self.interactive_sfd.setSceneRect(0, 0, self.size().width(), self.size().height())
        self.graphicsView_interactive_sfd.setScene(self.interactive_sfd)

    # Exclusively check buttons
    def on_pushbutton_add_stock_pushed(self):
        self.pushButton_add_flow.setChecked(False)
        self.pushButton_add_aux.setChecked(False)
        self.pushButton_add_connector.setChecked(False)

    def on_pushbutton_add_flow_pushed(self):
        self.pushButton_add_stock.setChecked(False)
        self.pushButton_add_aux.setChecked(False)
        self.pushButton_add_connector.setChecked(False)

    def on_pushbutton_add_aux_pushed(self):
        self.pushButton_add_stock.setChecked(False)
        self.pushButton_add_flow.setChecked(False)
        self.pushButton_add_connector.setChecked(False)

    def on_pushbutton_add_connector_pushed(self):
        self.pushButton_add_stock.setChecked(False)
        self.pushButton_add_flow.setChecked(False)
        self.pushButton_add_aux.setChecked(False)

    # def mousePressEvent(self, e):
    #     print(e.x(), e.y())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    main_window.setMinimumWidth(640)
    main_window.setMinimumHeight(480)
    wang_sim = WangSim()
    main_window.setCentralWidget(wang_sim)
    main_window.show()
    sys.exit(app.exec_())