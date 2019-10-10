import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from StockAndFlowInPython.sfd_canvas.interactive_sfd_ui import Ui_widget_interactive_sfd


class StockItem(QGraphicsRectItem):
    def __init__(self, rect, label):
        super(StockItem, self).__init__(rect)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.rect_circle = rect
        self.rect_text = None
        self.label = label

    def boundingRect(self):  # reload boundingRect() so that the bounding rect of label is added to the item's bounding rect
        original_bounding_rect = super(StockItem, self).boundingRect()  # bounding rect for the circle
        current_font = self.scene().font()
        font_metrics = QFontMetrics(current_font)  # calculator used to calculate text's bounding rect
        rect_text_origin = font_metrics.boundingRect(self.label)
        self.rect_text = QRectF(rect_text_origin.translated(
            self.rect_circle.x() + self.rect_circle.width() / 2 - rect_text_origin.width() / 2,
            self.rect_circle.y() + original_bounding_rect.height()+15))
        return original_bounding_rect.united(self.rect_text)

    def paint(self, painter, option, widget=None):
        super(StockItem, self).paint(painter, option, widget)
        painter.drawText(self.rect_text, self.label)


class AuxItem(QGraphicsEllipseItem):
    def __init__(self, rect, label):
        super(AuxItem, self).__init__(rect)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.rect_circle = rect
        self.rect_text = None
        self.label = label

    def boundingRect(self):
        # reload boundingRect() so that the bounding rect of label is added to the item's bounding rect
        original_bounding_rect = super(AuxItem, self).boundingRect()  # bounding rect for the circle
        current_font = self.scene().font()
        font_metrics = QFontMetrics(current_font)  # calculator used to calculate text's bounding rect
        rect_text_origin = font_metrics.boundingRect(self.label)
        self.rect_text = QRectF(rect_text_origin.translated(
            self.rect_circle.x() + self.rect_circle.width() / 2 - rect_text_origin.width() / 2,
            self.rect_circle.y() + original_bounding_rect.height() + 15))
        return original_bounding_rect.united(self.rect_text)

    def paint(self, painter, option, widget=None):
        super(AuxItem, self).paint(painter, option, widget)
        painter.drawText(self.rect_text, self.label)


class ModelCanvas(QGraphicsScene):
    def __init__(self):
        super(ModelCanvas, self).__init__()
        self.working_mode = None

    def mousePressEvent(self, e):
        print(self.working_mode)
        x = e.scenePos().x()
        y = e.scenePos().y()
        if self.working_mode == 'stock':
            self.add_stock(x, y)
        elif self.working_mode == 'aux':
            self.add_aux(x, y)
        super(ModelCanvas, self).mousePressEvent(e)  # this line is critical as it passes the event to the original func

    def add_stock(self, x, y, w=40, h=30, label='Stock'):
        qrect_stock = QRectF(x-w*0.5, y-h*0.5, w, h)
        self.addItem(StockItem(qrect_stock, label))

    def add_aux(self, x, y, r=15, label='Aux'):
        qrect_aux = QRectF(x-r*0.5, y-r*0.5, r, r)
        self.addItem(AuxItem(qrect_aux, label))


class InteractiveSFD(QWidget, Ui_widget_interactive_sfd):
    def __init__(self):
        super(InteractiveSFD, self).__init__()
        self.setupUi(self)
        self.pushButton_add_stock.setCheckable(True)
        self.pushButton_add_flow.setCheckable(True)
        self.pushButton_add_aux.setCheckable(True)
        self.pushButton_add_connector.setCheckable(True)

        self.pushButton_add_stock.clicked.connect(self.on_pushbutton_add_stock_pushed)
        self.pushButton_add_flow.clicked.connect(self.on_pushbutton_add_flow_pushed)
        self.pushButton_add_aux.clicked.connect(self.on_pushbutton_add_aux_pushed)
        self.pushButton_add_connector.clicked.connect(self.on_pushbutton_add_connector_pushed)

        self.model_canvas = ModelCanvas()
        self.graphicsView_interactive_sfd.setAcceptDrops(True)

        self.graphicsView_interactive_sfd.setSceneRect(0, 0, self.width(), self.height())
        self.graphicsView_interactive_sfd.setScene(self.model_canvas)
        self.graphicsView_interactive_sfd.show()

    # Exclusively check buttons
    def on_pushbutton_add_stock_pushed(self):
        self.model_canvas.working_mode = 'stock'
        self.pushButton_add_flow.setChecked(False)
        self.pushButton_add_aux.setChecked(False)
        self.pushButton_add_connector.setChecked(False)
        if not self.pushButton_add_stock.isChecked():
            self.model_canvas.working_mode = None

    def on_pushbutton_add_flow_pushed(self):
        self.model_canvas.working_mode = 'flow'
        self.pushButton_add_stock.setChecked(False)
        self.pushButton_add_aux.setChecked(False)
        self.pushButton_add_connector.setChecked(False)
        if not self.pushButton_add_flow.isChecked():
            self.model_canvas.working_mode = None

    def on_pushbutton_add_aux_pushed(self):
        self.model_canvas.working_mode = 'aux'
        self.pushButton_add_stock.setChecked(False)
        self.pushButton_add_flow.setChecked(False)
        self.pushButton_add_connector.setChecked(False)
        if not self.pushButton_add_aux.isChecked():
            self.model_canvas.working_mode = None

    def on_pushbutton_add_connector_pushed(self):
        self.model_canvas.working_mode = 'connector'
        self.pushButton_add_stock.setChecked(False)
        self.pushButton_add_flow.setChecked(False)
        self.pushButton_add_aux.setChecked(False)
        if not self.pushButton_add_connector.isChecked():
            self.model_canvas.working_mode = None


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    main_window.setWindowTitle("Interactive SFD")
    main_window.setMinimumWidth(640)
    main_window.setMinimumHeight(480)
    interactive_sfd = InteractiveSFD()
    main_window.setCentralWidget(interactive_sfd)
    main_window.show()
    sys.exit(app.exec_())