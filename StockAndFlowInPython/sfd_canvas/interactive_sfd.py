import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from StockAndFlowInPython.sfd_canvas.interactive_sfd_ui import Ui_widget_interactive_sfd


class StockItem(QGraphicsRectItem):
    def __init__(self, x, y, w, h, label):
        self.rect_rect = QRectF(x - w * 0.5, y - h * 0.5, w, h)
        super(StockItem, self).__init__(self.rect_rect)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.rect_text = None
        self.label = label

    def boundingRect(self):  # reload boundingRect() so that the bounding rect of label is added to the item's bounding rect
        original_bounding_rect = super(StockItem, self).boundingRect()  # bounding rect for the circle
        current_font = self.scene().font()
        font_metrics = QFontMetrics(current_font)  # calculator used to calculate text's bounding rect
        rect_text_origin = font_metrics.boundingRect(self.label)
        self.rect_text = QRectF(rect_text_origin.translated(
            int(self.rect_rect.x() + self.rect_rect.width() / 2 - rect_text_origin.width() / 2),
            int(self.rect_rect.y() + original_bounding_rect.height() + 15)))
        return original_bounding_rect.united(self.rect_text)

    def paint(self, painter, option, widget=None):
        super(StockItem, self).paint(painter, option, widget)
        painter.drawText(self.rect_text, self.label)


class FlowItem(QGraphicsItemGroup):
    def __init__(self, x, y, r, label):
        super(FlowItem, self).__init__()
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.central_point = QPointF(x, y)
        self.x = x
        self.y = y
        self.r = r
        self.label = label
        self.text_bounding_rect = None

        # circle
        self.circle_bounding_rect = QRectF(QPointF(self.x-self.r, self.y-self.r), QPointF(self.x+self.r, self.y+self.r))
        self.addToGroup(QGraphicsEllipseItem(self.circle_bounding_rect))

        # line
        self.p1 = QPointF(self.x-30, self.y)
        self.p2 = QPointF(self.x+30, self.y)
        self.l1 = QLineF(self.p1, self.p2)
        self.addToGroup(QGraphicsLineItem(self.l1))

        # arrow
        self.v = self.l1.unitVector()
        self.v.setLength(10)  # change the unit, => change the length of the arrow
        self.v.translate(60, 0)  # move v to the end of the line, should use relative coordinate as parameters
        self.n = self.v.normalVector()  # normal vector
        self.n.setLength(self.n.length()*0.5)  # width of the arrow
        self.n2 = self.n.normalVector().normalVector()  # an opposite vector of n

        self.end_arrow = QPolygonF()
        self.end_arrow.append(self.v.p2())
        self.end_arrow.append(self.n.p2())
        self.end_arrow.append(self.n2.p2())
        self.addToGroup(QGraphicsPolygonItem(self.end_arrow))  # TODO: need to figure out how to fill the arrow black

        # rectangle
        self.end_rect = QRectF(self.p1.x()-5, self.p1.y()-5, 10, 10)
        self.addToGroup(QGraphicsRectItem(self.end_rect))  # TODO: need to figure out how to fill the rectangle black

    def boundingRect(self):
        # this bounding rect should include 1) the circle 2) the arrow and line(s) 3) the label

        # label bounding rect
        current_font = self.scene().font()  # TODO: find out why call self.scene().font() in __init__() causes crash
        font_metrics = QFontMetrics(current_font)  # calculator used to calculate text's bounding rect
        original_text_bounding_rect = font_metrics.boundingRect(self.label)
        self.text_bounding_rect = QRectF(original_text_bounding_rect.translated(
            int(self.circle_bounding_rect.x() + self.circle_bounding_rect.width() / 2 - original_text_bounding_rect.width() / 2),
            int(self.circle_bounding_rect.y() + self.circle_bounding_rect.height() + 15)))
        return self.circle_bounding_rect.united(self.text_bounding_rect)

    def paint(self, painter, option, widget=None):
        painter.drawEllipse(self.central_point, self.r, self.r)
        painter.drawText(self.text_bounding_rect, self.label)


class AuxItem(QGraphicsEllipseItem):
    def __init__(self, x, y, r, label):
        self.circle_bounding_rect = QRectF(x - r, y - r, r*2, r*2)
        super(AuxItem, self).__init__(self.circle_bounding_rect)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.text_bounding_rect = None
        self.label = label

    def boundingRect(self):
        # reload boundingRect() so that the bounding rect of label is added to the item's bounding rect
        original_bounding_rect = super(AuxItem, self).boundingRect()  # bounding rect for the circle
        current_font = self.scene().font()
        font_metrics = QFontMetrics(current_font)  # calculator used to calculate text's bounding rect
        original_text_bounding_rect = font_metrics.boundingRect(self.label)
        self.text_bounding_rect = QRectF(original_text_bounding_rect.translated(
            int(self.circle_bounding_rect.x() + self.circle_bounding_rect.width() / 2 - original_text_bounding_rect.width() / 2),
            int(self.circle_bounding_rect.y() + original_bounding_rect.height() + 15)))
        return original_bounding_rect.united(self.text_bounding_rect)

    def paint(self, painter, option, widget=None):
        super(AuxItem, self).paint(painter, option, widget)
        painter.drawText(self.text_bounding_rect, self.label)


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
        elif self.working_mode == 'flow':
            self.add_flow(x, y)
        elif self.working_mode == 'aux':
            self.add_aux(x, y)
        super(ModelCanvas, self).mousePressEvent(e)  # this line is critical as it passes the event to the original func

    def add_stock(self, x, y, w=40, h=30, label='Stock'):
        self.addItem(StockItem(x=x, y=y, w=w, h=h, label=label))

    def add_flow(self, x, y, r=10, label='Flow'):
        self.addItem(FlowItem(x=x, y=y, r=r, label=label))

    def add_aux(self, x, y, r=10, label='Aux'):
        self.addItem(AuxItem(x=x, y=y, r=r, label=label))


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