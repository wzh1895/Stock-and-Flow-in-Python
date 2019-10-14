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
    core_move_signal = pyqtSignal(QPointF)

    def __init__(self, x, y, r, label):
        super(FlowCoreItem, self).__init__()
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.central_point = QPointF(x, y)
        self.x = x
        self.y = y
        self.r = r
        self.label = label
        self.text_bounding_rect = None  # we need to make it a property cuz drawing text needs it

        self.p1 = QPointF(self.x+30, self.y)  # arrow
        self.p2 = QPointF(self.x-30, self.y)  # rect
        print('Core, upon Creation: P1: {}, P2: {}'.format(self.p1, self.p2))
        self.l1 = QLineF(self.p1, self.p2)  # TODO update!

    def boundingRect(self):
        # this bounding rect should include 1) the circle 2) the label 3) the line
        # circle bounding rect
        circle_bounding_rect = QRectF(QPointF(self.x - self.r, self.y - self.r),
                                      QPointF(self.x + self.r, self.y + self.r))

        # label bounding rect
        # current_font = self.scene().font()  # TODO: find out why call self.scene().font() in __init__() causes crash
        font_1 = QFont('Calibri', 20)
        font_metrics = QFontMetrics(font_1)  # calculator used to calculate text's bounding rect
        original_text_bounding_rect = font_metrics.boundingRect(self.label)
        self.text_bounding_rect = QRectF(original_text_bounding_rect.translated(
            int(circle_bounding_rect.x() + circle_bounding_rect.width() / 2 - original_text_bounding_rect.width() / 2),
            int(circle_bounding_rect.y() + circle_bounding_rect.height() + 15)))

        # line bounding rect
        line_bounding_rect = QRectF(QPointF(self.p2.x()-5, self.p2.y()-5), QPointF(self.p1.x()+5, self.p1.y()+5))

        return circle_bounding_rect.united(line_bounding_rect).united(self.text_bounding_rect)

    def paint(self, painter, option, widget=None):
        print('Core: Updating core', self.p1, self.p2)
        self.l1 = QLineF(self.p1, self.p2)  # TODO update!
        painter.drawEllipse(self.central_point, self.r, self.r)
        painter.drawLine(self.l1)
        painter.drawText(self.text_bounding_rect, self.label)

    def mouseMoveEvent(self, event):
        super(FlowCoreItem, self).mouseMoveEvent(event)
        self.core_move_signal.emit(self.scenePos())  # send self's position to FlowItem. Come after super() for accuracy


class FlowRectItem(QGraphicsObject):  # Inherit from QGraphicsObject to use its signal-slot mechanism
    rect_move_signal = pyqtSignal(QPointF)

    def __init__(self, x, y):
        super(FlowRectItem, self).__init__()
        self.is_connected = False
        self.x = x
        self.y = y
        self.end_rect = QRectF(self.x - 5, self.y - 5, 10, 10)
        self.setFlag(QGraphicsItem.ItemIsMovable)

    def boundingRect(self):
        return self.end_rect

    def paint(self, painter, option, widget=None):
        painter.drawRect(self.end_rect)

    def mouseMoveEvent(self, event):
        super(FlowRectItem, self).mouseMoveEvent(event)
        self.rect_move_signal.emit(QPointF(self.x + self.pos().x(), self.y+self.pos().y()))


class FlowArrowItem(QGraphicsObject):  # Inherit from QGraphicsObject to use its signal-slot mechanism
    arrow_move_signal = pyqtSignal(QPointF)

    def __init__(self, x, y):
        super(FlowArrowItem, self).__init__()
        self.is_connected = False
        self.x = x
        self.y = y
        self.l1 = QLineF(QPointF(0, 0), QPointF(1, 0))
        self.v = self.l1.unitVector()
        self.v.setLength(10)  # change the unit, => change the length of the arrow
        self.v.translate(x, y)  # move v to the end of the line
        self.n = self.v.normalVector()  # normal vector
        self.n.setLength(self.n.length() * 0.5)  # width of the arrow
        self.n2 = self.n.normalVector().normalVector()  # an opposite vector of n

        self.end_arrow = QPolygonF()
        self.end_arrow.append(self.v.p2())
        self.end_arrow.append(self.n.p2())
        self.end_arrow.append(self.n2.p2())

        self.setFlag(QGraphicsItem.ItemIsMovable)

    def boundingRect(self):
        return QRectF(QPointF(self.x-10, self.y-10), QPointF(self.x+10, self.y+10))

    def paint(self, painter, option, widget=None):
        painter.drawPolygon(self.end_arrow)

    def mouseMoveEvent(self, event):
        super(FlowArrowItem, self).mouseMoveEvent(event)
        # here we send coordinates on canvas, instead of local
        self.arrow_move_signal.emit(QPointF(self.x + self.pos().x(), self.y+self.pos().y()))


class FlowItem(object):
    def __init__(self, canvas, x, y, r, label):  # this 'canvas' is the model_canvas itself, used for drawing
        super(FlowItem, self).__init__()
        self.core = FlowCoreItem(x=x, y=y, r=r, label=label)
        self.rect = FlowRectItem(x=x-30, y=y)
        self.arrow = FlowArrowItem(x=x+30, y=y)
        self.canvas = canvas
        self.canvas.addItem(self.core)
        self.canvas.addItem(self.rect)
        self.canvas.addItem(self.arrow)

        self.core.core_move_signal.connect(self.on_flow_core_move)
        self.rect.rect_move_signal.connect(self.on_flow_rect_move)
        self.arrow.arrow_move_signal.connect(self.on_flow_arrow_move)

    # The mechanism is:
    # 1) This FlowItem used for connecting the a) core 2) rect 3) arrow
    # 2) If neither Rect nor Arrow are connected to a stock, drag the core will move all three
    # 3) Drag the Rect or Arrow will move only the Rect or Arrow, and the line (inside the core) will be redrawn

    def on_flow_core_move(self, core_scene_pos):  # here we receive the offsets
        # print('Core pos:', core_scene_pos)
        core_x = core_scene_pos.x()
        core_y = core_scene_pos.y()
        if not self.arrow.is_connected and not self.rect.is_connected:
            self.rect.setPos(core_x, core_y)  # what we give are offsets
            self.arrow.setPos(core_x, core_y)  # what we give are offsets

    def on_flow_arrow_move(self, new_core_arrow_pos):
        # print('Arrow moving!')
        # print("Arrow New Position", new_core_arrow_pos)
        self.core.p1.setX(new_core_arrow_pos.x())
        self.core.p1.setY(new_core_arrow_pos.y())
        self.core.update()

    def on_flow_rect_move(self, new_core_rect_pos):
        # print('Rect moving!')
        # self.refresh_flow_line(new_rect_pos=core_rect_offset)
        self.core.p2.setX(new_core_rect_pos.x())
        self.core.p2.setY(new_core_rect_pos.y())
        self.core.update()


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
            int(self.circle_bounding_rect.x()
                + self.circle_bounding_rect.width() / 2
                - original_text_bounding_rect.width() / 2),
            int(self.circle_bounding_rect.y()
                + original_bounding_rect.height() + 15)))
        return original_bounding_rect.united(self.text_bounding_rect)

    def paint(self, painter, option, widget=None):
        super(AuxItem, self).paint(painter, option, widget)
        painter.drawText(self.text_bounding_rect, self.label)


class ModelCanvas(QGraphicsScene):
    def __init__(self):
        super(ModelCanvas, self).__init__()
        self.working_mode = None
        self.flows = dict()

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
        super(ModelCanvas, self).mousePressEvent(e)  # this line is critical as it passes the event to the original func

    def add_stock(self, x, y, w=40, h=30, label='Stock'):
        self.addItem(StockItem(x=x, y=y, w=w, h=h, label=label))

    def add_flow(self, x, y, r=10, label='Flow'):
        self.flows[label] = FlowItem(self, x, y, r, label)

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