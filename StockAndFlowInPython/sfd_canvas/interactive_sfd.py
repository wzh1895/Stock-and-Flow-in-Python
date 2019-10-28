import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from StockAndFlowInPython.sfd_canvas.interactive_sfd_ui import Ui_widget_interactive_sfd
from StockAndFlowInPython.graph_sd.graph_engine import STOCK, FLOW, VARIABLE, PARAMETER, ALIAS, CONNECTOR, Structure


class StockItem(QGraphicsRectItem):
    def __init__(self, w, h, label):
        self.rect_rect = QRectF(- w * 0.5, - h * 0.5, w, h)
        super(StockItem, self).__init__(self.rect_rect)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
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
        self.setFlag(QGraphicsObject.ItemIsMovable, True)
        self.setFlag(QGraphicsObject.ItemIsSelectable, True)
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

    def shape(self):
        path_0 = QPainterPath()
        path_0.addEllipse(self.central_point, self.r, self.r)
        return path_0

    def paint(self, painter, option, widget=None):
        painter.drawEllipse(self.central_point, self.r, self.r)
        painter.drawText(self.text_bounding_rect, self.label)

    def mouseMoveEvent(self, event):
        super(FlowCoreItem, self).mouseMoveEvent(event)
        self.core_move_signal.emit()  # send self's position to FlowItem. Come after super() for accuracy




class FlowRectItem(QGraphicsObject):  # Inherit from QGraphicsObject to use its signal-slot mechanism
    rect_move_signal = pyqtSignal(bool)

    def __init__(self):
        super(FlowRectItem, self).__init__()
        self.is_connected = False
        self.end_rect_point = QPointF(0, 0)
        self.end_rect = QRectF(self.end_rect_point.x() - 5, self.end_rect_point.y() - 5, 10, 10)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self.brush = QBrush(Qt.white)

    def boundingRect(self):
        return self.end_rect

    def paint(self, painter, option, widget=None):
        painter.setBrush(self.brush)
        painter.drawRect(self.end_rect)
        painter.drawPoint(self.end_rect_point)

    def mouseMoveEvent(self, event):
        collided_items = self.scene().collidingItems(self)
        stock_collided = False
        # print(collided_items)
        for item in collided_items:
            if type(item) == StockItem:
                self.brush = QBrush(Qt.black)
                stock_collided = True
        if stock_collided:
            self.is_connected = True
        else:
            self.is_connected = False
            self.brush = QBrush(Qt.white)

        super(FlowRectItem, self).mouseMoveEvent(event)
        self.rect_move_signal.emit(self.is_connected)


class FlowArrowItem(QGraphicsObject):  # Inherit from QGraphicsObject to use its signal-slot mechanism
    arrow_move_signal = pyqtSignal(bool)

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

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

        self.brush = QBrush(Qt.white)

    def boundingRect(self):
        return QRectF(QPointF(self.end_arrow_point.x()-10, self.end_arrow_point.y()-10),
                      QPointF(self.end_arrow_point.x()+10, self.end_arrow_point.y()+10))

    def paint(self, painter, option, widget=None):
        painter.setBrush(self.brush)
        painter.drawPolygon(self.end_arrow)
        painter.drawPoint(self.end_arrow_point)

    def mouseMoveEvent(self, event):
        collided_items = self.scene().collidingItems(self)
        stock_collided = False
        # print(collided_items)
        for item in collided_items:
            if type(item) == StockItem:
                self.brush = QBrush(Qt.black)
                stock_collided = True
        if stock_collided:
            self.is_connected = True
        else:
            self.is_connected = False
            self.brush = QBrush(Qt.white)

        super(FlowArrowItem, self).mouseMoveEvent(event)
        self.arrow_move_signal.emit(self.is_connected)


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
        line_bounding_rect = QRectF(QPointF(min_x-20, min_y-20), QPointF(max_x+20, max_y+20))
        return line_bounding_rect

    def paint(self, painter, option, widget=None):
        painter.setPen(QPen(Qt.black, 1))
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

    def on_flow_arrow_move(self, is_connected):
        if is_connected or self.rect.is_connected:
            self.core.setFlag(QGraphicsObject.ItemIsMovable, False)
        else:
            self.core.setFlag(QGraphicsObject.ItemIsMovable, True)
        self.line.p1 = self.arrow.pos() - self.line.pos()
        self.line.update()
        self.repose_flow_core()
        self.update_angle()

    def on_flow_rect_move(self, is_connected):
        if is_connected or self.arrow.is_connected:
            self.core.setFlag(QGraphicsObject.ItemIsMovable, False)
        else:
            self.core.setFlag(QGraphicsObject.ItemIsMovable, True)
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
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
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

    def shape(self):
        path_0 = QPainterPath()
        path_0.addEllipse(self.circle_bounding_rect)
        return path_0

    def paint(self, painter, option, widget=None):
        super(AuxItem, self).paint(painter, option, widget)
        painter.drawText(self.text_bounding_rect, self.label)


class ConnectorArrowItem(QGraphicsObject):
    connector_arrow_move_signal = pyqtSignal(bool)

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

        self.brush = QBrush(Qt.white)

    def boundingRect(self):
        return QRectF(QPointF(self.connector_end_arrow_point.x() - 10, self.connector_end_arrow_point.y() - 10),
                      QPointF(self.connector_end_arrow_point.x() + 10, self.connector_end_arrow_point.y() + 10))

    def shape(self):
        path_0 = QPainterPath()
        path_0.addPolygon(self.connector_end_arrow)
        return path_0

    def paint(self, painter, option, widget=None):
        painter.setBrush(self.brush)
        painter.setPen(QPen(Qt.blue, 1))
        painter.drawPolygon(self.connector_end_arrow)
        painter.drawPoint(self.connector_end_arrow_point)
        painter.setPen(QPen(Qt.black, 1))

    def mouseMoveEvent(self, event):
        collided_items = self.scene().collidingItems(self)
        stock_collided = False
        # print(collided_items)
        for item in collided_items:
            if type(item) in [FlowCoreItem, AuxItem]:
                self.brush = QBrush(Qt.blue)
                stock_collided = True
        if stock_collided:
            self.is_connected = True
        else:
            self.is_connected = False
            self.brush = QBrush(Qt.white)

        super(ConnectorArrowItem, self).mouseMoveEvent(event)
        self.connector_arrow_move_signal.emit(self.is_connected)


class ConnectorLineItem(QGraphicsObject):
    def __init__(self, delta_x, delta_y):
        super(ConnectorLineItem, self).__init__()
        self.p1 = QPointF(0, 0)  # root
        self.p2 = QPointF(delta_x, delta_y)  # end

    def boundingRect(self):
        min_x = min(self.p1.x(), self.p2.x())
        max_x = max(self.p1.x(), self.p2.x())
        min_y = min(self.p1.y(), self.p2.y())
        max_y = max(self.p1.y(), self.p2.y())
        line_bounding_rect = QRectF(QPointF(min_x-20, min_y-20), QPointF(max_x+20, max_y+20))
        return line_bounding_rect

    def paint(self, painter, option, widget=None):
        painter.setPen(QPen(Qt.blue, 1))
        line = QLineF(self.p1, self.p2)
        painter.drawLine(line)
        painter.setPen(QPen(Qt.black, 1))

    def shape(self):
        path_0 = QPainterPath()
        path_0.addEllipse(self.p1, 0, 0)  # add an ellipse that takes no place
        return path_0


class ConnectorArcItem(QGraphicsItem):
    def __init__(self, rect, start_angle, span_angle):
        super(ConnectorArcItem, self).__init__()
        self.rect = rect
        self.start_angle = start_angle
        self.span_angle = span_angle

    def boundingRect(self):
        return self.rect

    def shape(self):
        path_0 = QPainterPath()
        path_0.addEllipse(QPointF(0, 0), 0, 0)  # add an ellipse that takes no place
        return path_0

    def paint(self, painter, option, widget=None):
        painter.setPen(QPen(Qt.blue, 1))
        painter.drawArc(self.rect, self.start_angle, self.span_angle)
        painter.setPen(QPen(Qt.black, 1))


class ConnectorControllerItem(QGraphicsObject):
    connector_controller_move_signal = pyqtSignal()

    def __init__(self):
        super(ConnectorControllerItem, self).__init__()
        self.central_point = QPointF(0, 0)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

    def boundingRect(self):
        controller_bounding_rect = QRectF(-3, -3, 10, 10)
        return controller_bounding_rect

    def paint(self, painter, option, widget=None):
        painter.drawEllipse(self.central_point, 3, 3)

    def mouseMoveEvent(self, event):
        super(ConnectorControllerItem, self).mouseMoveEvent(event)
        self.connector_controller_move_signal.emit()


class ConnectorItem(object):
    def __init__(self, canvas, from_x, from_y, to_x=None, to_y=None, angle=0):
        super(ConnectorItem, self).__init__()
        self.starting_point = QPointF(from_x, from_y)
        if to_x is not None and to_y is not None:
            delta_x = to_x - from_x
            delta_y = to_y - from_y
        else:
            delta_x = 0
            delta_y = 0

        self.angle = angle

        self.line = ConnectorLineItem(delta_x=delta_x, delta_y=delta_y)
        self.line.setPos(self.starting_point)
        # self.line.setVisible(False)  # by default, the line is not visible; only when it's really a straight line
        self.arc = ConnectorArcItem(QRectF(0, 0, 0, 0), 0, 0)
        self.controller = ConnectorControllerItem()
        self.controller.setPos(from_x, from_y)
        self.arrow = ConnectorArrowItem()
        self.arrow.setPos(QPointF(from_x + delta_x, from_y + delta_y))
        self.update_arrow_angle_arc()

        self.canvas = canvas
        self.canvas.addItem(self.arc)
        self.canvas.addItem(self.controller)
        self.canvas.addItem(self.line)
        self.canvas.addItem(self.arrow)

        self.arrow.connector_arrow_move_signal.connect(self.on_connector_arrow_move)
        self.controller.connector_controller_move_signal.connect(self.on_connector_controller_move)

    def on_connector_controller_move(self):
        self.update_line()
        self.update_arc()

    def on_connector_arrow_move(self, is_connected):
        self.update_line()
        self.update_arc()

    def update_line(self):
        self.line.p2 = self.arrow.pos() - self.line.pos()
        self.line.update()
        self.update_arrow_angle_line()

    def update_arc(self):
        # re-draw the connector line
        center, r = self.calculate_circle(self.starting_point, self.controller.scenePos(), self.arrow.scenePos())
        # print(center, r)
        if center is None and r is None:
            self.arc.setVisible(False)
            self.line.setVisible(True)
        else:
            self.line.setVisible(False)
            self.arc.setVisible(True)
            new_rect_for_arc = QRectF(center.x() - r, center.y() - r, r * 2, r * 2)
            self.arc.rect = new_rect_for_arc
            new_start_angle = QLineF(center, self.arrow.scenePos()).angle() * 16
            new_span_angle = QLineF(center, self.starting_point).angle() * 16 - new_start_angle
            if new_span_angle > 180 * 16:
                new_span_angle = new_span_angle - 360 * 16  # This is to control that we always have an arc < 180
            self.arc.start_angle = new_start_angle
            self.arc.span_angle = new_span_angle
            # print('Start angle {}, span angle {}'.format(new_start_angle/16, new_span_angle/16))
            self.arc.update()
            self.update_arrow_angle_arc()

    def update_arrow_angle_line(self):
        self.angle = QLineF(self.starting_point, self.arrow.scenePos()).angle()
        self.arrow.setRotation(-1 * self.angle)

    def update_arrow_angle_arc(self):
        if self.arc.start_angle == 0:  # just created
            self.angle = 0
        elif self.arc.span_angle < 0:
            self.angle = self.arc.start_angle / 16 + 90
        else:
            self.angle = self.arc.start_angle / 16 - 90
        self.arrow.setRotation(-1*self.angle)

    @staticmethod
    def calculate_circle(pt1, pt2, pt3):
        a = pt1.x() - pt2.x()
        b = pt1.y() - pt2.y()
        c = pt1.x() - pt3.x()
        d = pt1.y() - pt3.y()
        e = ((pt1.x() ** 2 - pt2.x() ** 2) + (pt1.y() ** 2 - pt2.y() ** 2)) / 2
        f = ((pt1.x() ** 2 - pt3.x() ** 2) + (pt1.y() ** 2 - pt3.y() ** 2)) / 2
        delta = b * c - a * d
        # print('\n', delta)
        if abs(delta) < 200:  # the three points are on the same line
            return None, None
        x0 = - (d * e - b * f) / delta
        y0 = - (a * f - c * e) / delta
        r = ((pt1.x() - x0) ** 2 + (pt1.y() - y0) ** 2) ** 0.5
        return QPointF(x0, y0), r


class ModelCanvas(QGraphicsScene):
    def __init__(self, parent):
        super(ModelCanvas, self).__init__()
        self.setParent(parent)
        self.working_mode = None
        self.flows = dict()
        self.connectors = dict()

        self.stock_uid = 1
        self.flow_uid = 1
        self.aux_uid = 1
        self.connector_uid = 1

    def mousePressEvent(self, e):
        # print(self.working_mode)
        x = e.scenePos().x()
        y = e.scenePos().y()
        if self.working_mode == 'stock':
            self.add_stock(x, y)
            self.working_mode = None
        elif self.working_mode == 'flow':
            self.add_flow(x, y)
            self.working_mode = None
        elif self.working_mode == 'aux':
            self.add_aux(x, y)
            self.working_mode = None
        elif self.working_mode == 'connector':
            # check if there is a stock/flow/aux at this point; if not, do nothing.
            items_at_click_point = self.itemAt(x, y, QTransform())
            print('Items at clicking point', items_at_click_point)
            if type(items_at_click_point) in [StockItem,
                                              FlowCoreItem,
                                              FlowLineItem,  # TODO: solve the overlap of FlowLine and FlowCore
                                              AuxItem]:
                self.draw_connector(x, y)
                self.working_mode = None

        super(ModelCanvas, self).mousePressEvent(e)  # this line is critical as it passes the event to the original func
        self.parent().reset_all_buttons()

    def add_stock(self, x, y, w=40, h=30, label=None):
        if label is None:
            label = self.ask_for_name()
            if label is None:
                label = 'Stock' + str(self.stock_uid)

        stock_item = StockItem(w=w, h=h, label=label)
        stock_item.setPos(x, y)
        self.addItem(stock_item)
        self.stock_uid += 1

    def add_flow(self, x, y, r=10, label=None):
        if label is None:
            label = self.ask_for_name()
            if label is None:
                label = 'Flow' + str(self.flow_uid)

        self.flows[label] = FlowItem(self, x, y, r, label)
        self.flow_uid += 1

    def add_aux(self, x, y, r=10, label=None):
        if label is None:
            label = self.ask_for_name()
            if label is None:
                label = 'Aux' + str(self.aux_uid)

        aux_item = AuxItem(r=r, label=label)
        aux_item.setPos(x, y)
        self.addItem(aux_item)
        self.aux_uid += 1

    def draw_connector(self, x, y, angle=0):
        self.connectors[self.connector_uid] = ConnectorItem(self, x, y, angle=angle)
        self.connector_uid += 1

    def add_connector(self, from_x, from_y, to_x, to_y, angle):
        print(from_x, from_y, to_x, to_y, angle)
        self.connectors[self.connector_uid] = ConnectorItem(self, from_x, from_y, to_x, to_y, angle=angle)
        self.connector_uid += 1

    def ask_for_name(self):
        name, ok = QInputDialog.getText(self.parent(), 'Input', 'Input variable name:')
        if ok:
            return name
        else:
            return None


class InteractiveSFD(QWidget, Ui_widget_interactive_sfd):
    def __init__(self):
        # print('Initializing Interactive SFD')
        super(InteractiveSFD, self).__init__()
        self.setupUi(self)
        self.pushButton_add_stock.setCheckable(True)
        self.pushButton_add_flow.setCheckable(True)
        self.pushButton_add_aux.setCheckable(True)
        self.pushButton_add_connector.setCheckable(True)

        self.pushButton_add_stock.clicked.connect(self.on_pushbutton_add_stock_clicked)
        self.pushButton_add_flow.clicked.connect(self.on_pushbutton_add_flow_clicked)
        self.pushButton_add_aux.clicked.connect(self.on_pushbutton_add_aux_clicked)
        self.pushButton_add_connector.clicked.connect(self.on_pushbutton_add_connector_clicked)

        self.model_canvas = ModelCanvas(self)
        self.graphicsView_interactive_sfd.setAcceptDrops(True)

        self.graphicsView_interactive_sfd.setSceneRect(0, 0, self.width(), self.height())
        self.graphicsView_interactive_sfd.setScene(self.model_canvas)
        self.graphicsView_interactive_sfd.show()

        self.model_structure = Structure()

    # Exclusively check buttons
    def on_pushbutton_add_stock_clicked(self):
        self.model_canvas.working_mode = 'stock'
        self.pushButton_add_flow.setChecked(False)
        self.pushButton_add_aux.setChecked(False)
        self.pushButton_add_connector.setChecked(False)
        if not self.pushButton_add_stock.isChecked():
            self.model_canvas.working_mode = None

    def on_pushbutton_add_flow_clicked(self):
        self.model_canvas.working_mode = 'flow'
        self.pushButton_add_stock.setChecked(False)
        self.pushButton_add_aux.setChecked(False)
        self.pushButton_add_connector.setChecked(False)
        if not self.pushButton_add_flow.isChecked():
            self.model_canvas.working_mode = None

    def on_pushbutton_add_aux_clicked(self):
        self.model_canvas.working_mode = 'aux'
        self.pushButton_add_stock.setChecked(False)
        self.pushButton_add_flow.setChecked(False)
        self.pushButton_add_connector.setChecked(False)
        if not self.pushButton_add_aux.isChecked():
            self.model_canvas.working_mode = None

    def on_pushbutton_add_connector_clicked(self):
        self.model_canvas.working_mode = 'connector'
        self.pushButton_add_stock.setChecked(False)
        self.pushButton_add_flow.setChecked(False)
        self.pushButton_add_aux.setChecked(False)
        if not self.pushButton_add_connector.isChecked():
            self.model_canvas.working_mode = None

    def reset_all_buttons(self):
        self.pushButton_add_stock.setChecked(False)
        self.pushButton_add_flow.setChecked(False)
        self.pushButton_add_aux.setChecked(False)
        self.pushButton_add_connector.setChecked(False)

    @staticmethod
    def name_handler(name):
        return name.replace(' ', '_').replace('\n', '_')

    def locate_var(self, ele):
        for element in self.model_structure.sfd.nodes:
            if element == ele:
                x = self.model_structure.sfd.nodes[element]['pos'][0]
                y = self.model_structure.sfd.nodes[element]['pos'][1]
                return [float(x), float(y)]

        # if nothing is found (return is not triggered), try replace ' ' with '_'
        name = self.name_handler(ele)

        for element in self.model_structure.sfd.nodes:
            if element == ele:
                x = self.model_structure.sfd.nodes[element]['pos'][0]
                y = self.model_structure.sfd.nodes[element]['pos'][1]
                return [float(x), float(y)]

    def draw_existing_sfd(self, sfd):
        print('drawing sfd')
        self.model_structure = sfd

        radius1 = 8

        # draw flows
        for element in self.model_structure.sfd.nodes:
            if self.model_structure.sfd.nodes[element]['element_type'] == FLOW:
                print("    drawing flow {}".format(element))
                x = self.model_structure.sfd.nodes[element]['pos'][0]
                y = self.model_structure.sfd.nodes[element]['pos'][1]
                points = self.model_structure.sfd.nodes[element]['points']
                self.model_canvas.add_flow(x, y, label=element)

        # draw stocks (comes the last, so they can cover the connectors)
        for element in self.model_structure.sfd.nodes:
            if self.model_structure.sfd.nodes[element]['element_type'] == STOCK:
                print("    drawing stock {}".format(element))
                x = self.model_structure.sfd.nodes[element]['pos'][0]
                y = self.model_structure.sfd.nodes[element]['pos'][1]
                # print(x,y)
                self.model_canvas.add_stock(x, y, label=element)

        # draw auxiliaries
        for element in self.model_structure.sfd.nodes:
            if self.model_structure.sfd.nodes[element]['element_type'] in [PARAMETER, VARIABLE]:
                print("    drawing {} {}".format(self.model_structure.sfd.nodes[element]['element_type'], element))
                x = self.model_structure.sfd.nodes[element]['pos'][0]
                y = self.model_structure.sfd.nodes[element]['pos'][1]
                self.model_canvas.add_aux(x, y, label=element)

        # draw connectors
        # print('SFD:', self.model_structure.sfd.nodes(data=True))
        for connector in self.model_structure.sfd.edges():
            from_element = connector[0]
            # print('from ele', from_element)
            to_element = connector[1]
            # print('to ele', to_element)
            if self.model_structure[from_element][to_element]['display']:
                # Only draw when 'display' == True, avoid FLOW--->STOCK
                print('    drawing connector from {} to {}'.format(from_element, to_element))
                from_cord = self.locate_var(from_element)
                # print('from cord', from_cord)
                to_cord = self.locate_var(to_element)
                # print('to cord', to_cord)
                angle = self.model_structure[from_element][to_element]['angle']
                self.model_canvas.add_connector(from_cord[0], from_cord[1], to_cord[0], to_cord[1], angle)


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
