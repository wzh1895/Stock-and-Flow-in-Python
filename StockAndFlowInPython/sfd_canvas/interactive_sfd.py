import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from StockAndFlowInPython.sfd_canvas.interactive_sfd_ui import Ui_widget_interactive_sfd


class StockItem(QGraphicsRectItem):
    def __init__(self, w, h, label):
        self.rect_rect = QRectF(- w * 0.5, - h * 0.5, w, h)
        super(StockItem, self).__init__(self.rect_rect)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.rect_text = None
        self.label = label

    def boundingRect(self):  # reload boundingRect() to add the label's bounding rect to the item's bounding rect
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


class FlowCoreItem(QGraphicsObject):  # Inherit from QGraphicsObject to use its signal-slot mechanism
    core_move_signal = pyqtSignal()
    arrow_direction_change_signal = pyqtSignal(QVector2D)

    def __init__(self, r, label):
        super(FlowCoreItem, self).__init__()
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.central_point = QPointF(0, 0)
        self.label = label
        self.r = r
        self.text_bounding_rect = None  # we need to make it a property cuz drawing text needs it

        self.p1 = QPointF(30, 0)
        self.p2 = QPointF(-30, 0)

    def boundingRect(self):
        # this bounding rect should include 1) the circle 2) the label
        # circle bounding rect
        circle_bounding_rect = QRectF(QPointF(self.central_point.x() - self.r, self.central_point.y() - self.r),
                                      QPointF(self.central_point.x() + self.r, self.central_point.y() + self.r))

        # label bounding rect
        current_font = self.scene().font()  # TODO: find out why call self.scene().font() in __init__() causes crash
        font_metrics = QFontMetrics(current_font)  # calculator used to calculate text's bounding rect
        original_text_bounding_rect = font_metrics.boundingRect(self.label)
        self.text_bounding_rect = QRectF(original_text_bounding_rect.translated(
            int(circle_bounding_rect.x() + circle_bounding_rect.width() / 2 - original_text_bounding_rect.width() / 2),
            int(circle_bounding_rect.y() + circle_bounding_rect.height() + 15)))

        return circle_bounding_rect.united(self.text_bounding_rect)

    def paint(self, painter, option, widget=None):
        painter.setPen(QPen(Qt.black, 2))
        painter.drawEllipse(self.central_point, self.r, self.r)
        painter.setPen(QPen(Qt.black, 1))
        painter.drawText(self.text_bounding_rect, self.label)

    def mouseMoveEvent(self, event):
        super(FlowCoreItem, self).mouseMoveEvent(event)
        self.core_move_signal.emit()  # send self's position to FlowItem. Come after super() for accuracy


class FlowRectItem(QGraphicsObject):  # Inherit from QGraphicsObject to use its signal-slot mechanism
    rect_move_signal = pyqtSignal()

    def __init__(self):
        super(FlowRectItem, self).__init__()
        self.is_connected = False
        self.end_rect_point = QPointF(0, 0)
        self.end_rect = QRectF(self.end_rect_point.x() - 5, self.end_rect_point.y() - 5, 10, 10)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

    def boundingRect(self):
        return self.end_rect

    def paint(self, painter, option, widget=None):
        painter.drawRect(self.end_rect)
        painter.drawPoint(self.end_rect_point)

    def mouseMoveEvent(self, event):
        super(FlowRectItem, self).mouseMoveEvent(event)
        self.rect_move_signal.emit()


class FlowArrowItem(QGraphicsObject):  # Inherit from QGraphicsObject to use its signal-slot mechanism
    arrow_move_signal = pyqtSignal()

    def __init__(self):
        super(FlowArrowItem, self).__init__()
        self.is_connected = False
        self.end_arrow_point = QPointF(0, 0)
        self.l1 = QLineF(QPointF(0, 0), QPointF(1, 0))
        self.v = self.l1.unitVector()
        self.v.setLength(10)  # change the unit, => change the length of the arrow
        self.v.translate(self.end_arrow_point)  # move v to the end of the line
        self.n = self.v.normalVector()  # normal vector
        self.n.setLength(self.n.length() * 0.5)  # width of the arrow
        self.n2 = self.n.normalVector().normalVector()  # an opposite vector of n

        self.end_arrow = QPolygonF()
        self.end_arrow.append(self.v.p2())
        self.end_arrow.append(self.n.p2())
        self.end_arrow.append(self.n2.p2())

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

    def boundingRect(self):
        return QRectF(QPointF(self.end_arrow_point.x()-10, self.end_arrow_point.y()-10),
                      QPointF(self.end_arrow_point.x()+10, self.end_arrow_point.y()+10))

    def paint(self, painter, option, widget=None):
        painter.drawPolygon(self.end_arrow)
        painter.drawPoint(self.end_arrow_point)

    def mouseMoveEvent(self, event):
        super(FlowArrowItem, self).mouseMoveEvent(event)
        self.arrow_move_signal.emit()


class FlowLineItem(QGraphicsObject):
    def __init__(self):
        super(FlowLineItem, self).__init__()
        self.p1 = QPointF(30, 0)
        self.p2 = QPointF(-30, 0)

    def boundingRect(self):
        min_x = min(self.p1.x(), self.p2.x())
        max_x = max(self.p1.x(), self.p2.x())
        min_y = min(self.p1.y(), self.p2.y())
        max_y = max(self.p1.y(), self.p2.y())
        line_bounding_rect = QRectF(QPointF(min_x-10, min_y-10), QPointF(max_x+10, max_y+10))
        return line_bounding_rect

    def paint(self, painter, option, widget=None):
        painter.setPen(QPen(Qt.black, 2))
        line = QLineF(self.p1, self.p2)
        painter.drawLine(line)
        painter.setPen(QPen(Qt.black, 1))


class FlowItem(object):
    def __init__(self, canvas, x, y, r, label):  # this 'canvas' is the model_canvas itself, used for drawing
        super(FlowItem, self).__init__()
        self.core = FlowCoreItem(r=r, label=label)
        self.core.setPos(x, y)
        self.rect = FlowRectItem()
        self.rect.setPos(x-30, y)
        self.arrow = FlowArrowItem()
        self.arrow.setPos(x+30, y)
        self.line = FlowLineItem()
        self.line.setPos(x, y)
        self.canvas = canvas
        self.canvas.addItem(self.core)
        self.canvas.addItem(self.rect)
        self.canvas.addItem(self.arrow)
        self.canvas.addItem(self.line)

        self.from_core_to_arrow = self.arrow.pos() - self.core.pos()
        self.from_core_to_rect = self.rect.pos() - self.core.pos()
        self.from_core_to_line = self.line.pos() - self.core.pos()

        self.angle = 0

        self.core.core_move_signal.connect(self.on_flow_core_move)
        self.rect.rect_move_signal.connect(self.on_flow_rect_move)
        self.arrow.arrow_move_signal.connect(self.on_flow_arrow_move)

    def on_flow_core_move(self):  # here we receive the offsets
        self.arrow.setPos(self.core.pos() + self.from_core_to_arrow)
        self.rect.setPos(self.core.pos() + self.from_core_to_rect)
        self.line.setPos(self.core.pos() + self.from_core_to_line)

    def on_flow_arrow_move(self):
        self.line.p1 = self.arrow.pos() - self.line.pos()
        self.line.update()
        self.repose_flow_core()
        self.update_angle()

    def on_flow_rect_move(self):
        self.line.p2 = self.rect.pos() - self.line.pos()
        self.line.update()
        self.repose_flow_core()
        self.update_angle()

    def repose_flow_core(self):
        self.core.setPos((self.arrow.pos().x()+self.rect.pos().x())/2, (self.arrow.pos().y()+self.rect.pos().y())/2)
        self.update_relative_distance()

    def update_relative_distance(self):
        self.from_core_to_arrow = self.arrow.pos() - self.core.pos()
        self.from_core_to_rect = self.rect.pos() - self.core.pos()
        self.from_core_to_line = self.line.pos() - self.core.pos()

    def update_angle(self):
        self.angle = QLineF(self.line.p2, self.line.p1).angle()
        self.arrow.setRotation(-1*self.angle)


class AuxItem(QGraphicsEllipseItem):
    def __init__(self, r, label):
        self.circle_bounding_rect = QRectF(- r, - r, r*2, r*2)
        super(AuxItem, self).__init__(self.circle_bounding_rect)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.text_bounding_rect = None
        self.label = label

    def boundingRect(self):
        # reload boundingRect() so that the bounding rect of label is added to the item's bounding rect
        original_bounding_rect = super(AuxItem, self).boundingRect()  # bounding rect for the circle
        current_font = self.scene().font()
        font_metrics = QFontMetrics(current_font)  # calculator used to calculate text's bounding rect
        original_text_bounding_rect = font_metrics.boundingRect(self.label)
        self.text_bounding_rect = QRectF(original_text_bounding_rect.translated(
            int(self.circle_bounding_rect.x()
                + self.circle_bounding_rect.width() / 2
                - original_text_bounding_rect.width() / 2),
            int(self.circle_bounding_rect.y()
                + original_bounding_rect.height() + 15)))
        return original_bounding_rect.united(self.text_bounding_rect)

    def paint(self, painter, option, widget=None):
        super(AuxItem, self).paint(painter, option, widget)
        painter.drawText(self.text_bounding_rect, self.label)


class ConnectorArrowItem(QGraphicsObject):
    connector_arrow_move_signal = pyqtSignal()

    def __init__(self):
        super(ConnectorArrowItem, self).__init__()
        self.is_connected = False
        self.connector_end_arrow_point = QPointF(0, 0)
        self.l1 = QLineF(QPointF(0, 0), QPointF(1, 0))
        self.v = self.l1.unitVector()
        self.v.setLength(10)  # change the unit, => change the length of the arrow
        self.v.translate(self.connector_end_arrow_point)  # move v to the end of the line
        self.n = self.v.normalVector()  # normal vector
        self.n.setLength(self.n.length() * 0.5)  # width of the arrow
        self.n2 = self.n.normalVector().normalVector()  # an opposite vector of n

        self.connector_end_arrow = QPolygonF()
        self.connector_end_arrow.append(self.v.p2())
        self.connector_end_arrow.append(self.n.p2())
        self.connector_end_arrow.append(self.n2.p2())

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

    def boundingRect(self):
        return QRectF(QPointF(self.connector_end_arrow_point.x() - 10, self.connector_end_arrow_point.y() - 10),
                      QPointF(self.connector_end_arrow_point.x() + 10, self.connector_end_arrow_point.y() + 10))

    def paint(self, painter, option, widget=None):
        painter.setPen(QPen(Qt.red, 1))
        painter.drawPolygon(self.connector_end_arrow)
        painter.drawPoint(self.connector_end_arrow_point)
        painter.setPen(QPen(Qt.black, 1))

    def mouseMoveEvent(self, event):
        super(ConnectorArrowItem, self).mouseMoveEvent(event)
        self.connector_arrow_move_signal.emit()


class ConnectorLineItem(QGraphicsObject):
    def __init__(self):
        super(ConnectorLineItem, self).__init__()
        self.p1 = QPointF(0, 0)
        self.p2 = QPointF(0, 0)

    def boundingRect(self):
        min_x = min(self.p1.x(), self.p2.x())
        max_x = max(self.p1.x(), self.p2.x())
        min_y = min(self.p1.y(), self.p2.y())
        max_y = max(self.p1.y(), self.p2.y())
        line_bounding_rect = QRectF(QPointF(min_x-10, min_y-10), QPointF(max_x+10, max_y+10))
        return line_bounding_rect

    def paint(self, painter, option, widget=None):
        painter.setPen(QPen(Qt.red, 1))
        line = QLineF(self.p1, self.p2)
        painter.drawLine(line)
        painter.setPen(QPen(Qt.black, 1))


class ConnectorItem(object):
    def __init__(self, canvas, x, y, angle):
        super(ConnectorItem, self).__init__()
        self.starting_point = QPointF(x, y)
        self.angle = angle

        self.arrow = ConnectorArrowItem()
        self.arrow.setPos(self.starting_point)
        self.line = ConnectorLineItem()
        self.line.setPos(self.starting_point)
        self.canvas = canvas
        self.canvas.addItem(self.arrow)
        self.canvas.addItem(self.line)

        self.arrow.connector_arrow_move_signal.connect(self.on_connector_arrow_move)

    def on_connector_arrow_move(self):
        self.line.p2 = self.arrow.pos() - self.line.pos()
        self.line.update()


class ModelCanvas(QGraphicsScene):
    def __init__(self):
        super(ModelCanvas, self).__init__()
        self.working_mode = None
        self.flows = dict()
        self.connectors = dict()

        self.uid = 1

    def mousePressEvent(self, e):
        # print(self.working_mode)
        x = e.scenePos().x()
        y = e.scenePos().y()
        if self.working_mode == 'stock':
            self.add_stock(x, y)
        elif self.working_mode == 'flow':
            self.add_flow(x, y)
        elif self.working_mode == 'aux':
            self.add_aux(x, y)
        elif self.working_mode == 'connector':
            self.add_connector(x, y)
        super(ModelCanvas, self).mousePressEvent(e)  # this line is critical as it passes the event to the original func

    def add_stock(self, x, y, w=40, h=30, label='Stock'):
        stock_item = StockItem(w=w, h=h, label=label)
        stock_item.setPos(x, y)
        self.addItem(stock_item)

    def add_flow(self, x, y, r=10, label='Flow'):
        self.flows[label] = FlowItem(self, x, y, r, label)

    def add_aux(self, x, y, r=10, label='Aux'):
        aux_item = AuxItem(r=r, label=label)
        aux_item.setPos(x, y)
        self.addItem(aux_item)

    def add_connector(self, x, y, angle=0):
        # connect to the uid system later
        self.connectors[self.uid] = ConnectorItem(self, x, y, angle)
        self.uid += 1


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
