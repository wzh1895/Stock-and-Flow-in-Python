from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from StockAndFlowInPython.graph_sd.graph_based_engine import STOCK, FLOW, VARIABLE, PARAMETER, ALIAS
import math
import sys


class SFDCanvas(QWidget):
    def __init__(self):
        super(SFDCanvas, self).__init__()
        self.xmost = 300
        self.ymost = 300
        self.sfd = None

    @staticmethod
    def name_handler(name):
        return name.replace(' ', '_').replace('\n', '_')

    def draw_sfd(self, sfd):
        """
        Receive a graph representation of SFD and draw it on canvas
        :param sfd: Graph network
        :return:
        """
        self.sfd = sfd
        self.repaint()

    def reset_canvas(self):
        pass

    def locate_var(self, name):
        name = self.name_handler(name)
        # print("locating...")
        # print(name)
        # print(self.session_handler1.model_structure.sfd.nodes)
        for element in self.sfd.nodes:
            if element == name:
                x = self.sfd.nodes[element]['pos'][0]
                y = self.sfd.nodes[element]['pos'][1]
                return [float(x), float(y)]

    def create_stock(self, qp, x, y, w, h, label):
        """
        Center x, Center y, width, height, label
        """
        qp.setBrush(QColor(255, 255, 255))
        qp.drawRect(x - w * 0.5, y - h * 0.5, w, h)
        qp.drawText(QRect(x - 30 - w * 0.5, y + 30 - h * 0.5, w + 60, h),
                    Qt.AlignCenter,
                    label)

    def create_flow(self, qp, x, y, pts, r, label):
        """
        Starting point x, y, ending point x, y, length, circle radius, label
        """
        for i in range(len(pts) - 1):
            source = QPointF(pts[i][0], pts[i][1])
            dest = QPointF(pts[i + 1][0], pts[i + 1][1])
            line = QLineF(source, dest)
            qp.drawLine(line)
            if i == len(pts) - 2:  # if this is the last line
                # draw an arrow
                self.create_arrow(qp, source.x(), source.y(), dest.x(), dest.y())

        qp.drawEllipse(QRect(x - r, y - r, r*2, r*2))
        qp.drawText(QRect(x-30, y+7, 60, 30), Qt.AlignCenter, label)

    def create_aux(self, qp, x, y, r, label):
        """
        Central point x, y, radius, label
        """
        qp.drawEllipse(QRect(x - r, y - r, r*2, r*2))
        qp.drawText(QRect(x-30, y+7, 60, 30), Qt.AlignCenter, label)

    def create_alias(self, qp, x, y, r, label):
        """
        Central point x, y, radius, label
        """
        qp.drawEllipse(QRect(x - r, y - r, r * 2, r * 2))

        # dealing with the italic style of an alias' label
        font_0 = qp.font()
        font_0.setItalic(True)
        qp.setFont(font_0)
        qp.drawText(QRect(r - 30, y + 7, 60, 30), Qt.AlignCenter, label)
        font_0.setItalic(False)
        qp.setFont(font_0)

    def create_connector(self, qp, x_a, y_a, x_b, y_b, angle=None):
        if angle is None:
            self.create_arrow(qp, x_a, y_a, x_b, y_b)
        else:
            alpha = math.radians(angle)
            if math.pi < alpha < math.pi * 2:
                alpha -= math.pi * 2

            # calculate the center of circle

            rad_radiusA = alpha - math.pi * 0.5  # radiant of radius of the circle going out from A
            gA = math.tan(rad_radiusA)
            if x_b != x_a:
                gAB = (y_a - y_b) / (x_b - x_a)  # y axis inversed, could be 'zero division'
            else:
                gAB = 99.99

            gM = (-1) / gAB
            xM = (x_a + x_b) / 2
            yM = (y_a + y_b) / 2

            xC = (y_a + gA * x_a - gM * xM - yM) / (gA - gM)
            yC = y_a - gA * (xC - x_a)
            # TODO: when C and A are calculated to be the same point (and in fact not)
            rad_CA = math.atan2((yC - y_a), (x_a - xC))
            rad_CB = math.atan2((yC - y_b), (x_b - xC))

            # calculate radius

            radius = (pow((x_b - xC), 2) + pow((yC - y_b), 2)) ** 0.5
            baseArc = math.atan2(yC - y_a, x_a - xC)

            vecStarting = [math.cos(alpha), math.sin(alpha)]
            vecAtoB = [x_b - x_a, y_a - y_b]
            angleCos = self.cos_formula(vecStarting, vecAtoB)

            inverse = 1

            if angleCos < 0:  # you hu
                # print('deg_CA, ', math.degrees(rad_CA),'deg_CB',math.degrees(rad_CB))
                diff = rad_CB - rad_CA
                # print('youhu')
            else:  # lie hu
                if rad_CA * rad_CB < 0 and rad_CA <= rad_CB:  # yi hao
                    diff = rad_CB - rad_CA
                    if diff > math.pi:
                        diff = abs(diff) - math.pi * 2
                elif rad_CA * rad_CB < 0 and rad_CA > rad_CB:
                    diff = math.pi * 2 - rad_CA + rad_CB
                    if diff > math.pi:
                        diff = diff - math.pi * 2
                elif rad_CA * rad_CB > 0 and rad_CA > rad_CB:
                    diff = rad_CB - rad_CA
                    if diff > math.pi:
                        diff = math.pi * 2 - diff
                elif rad_CA * rad_CB > 0 and rad_CA < rad_CB:
                    diff = rad_CB - rad_CA
                    if diff > math.pi:
                        diff = math.pi * 2 - diff
                else:
                    diff = rad_CB - rad_CA
                # print('liehu')

            # generate new points

            x = [x_a]
            y = [y_a]
            points = [(x_a, y_a)]
            n = 7

            for i in range(n):
                baseArc = baseArc + diff / (n + 1) * inverse
                x1 = xC + radius * math.cos(baseArc)
                y1 = yC - radius * math.sin(baseArc)
                x.append(x1)
                y.append(y1)
                points.append((xC + radius * math.cos(baseArc), yC - radius * math.sin(baseArc)))

                # Draw dots of the connectors, if you would like
                # self.create_dot(x1,y1,2,'gray',str(i))

            x.append(x_b)
            y.append(y_b)
            points.append((x_b, y_b))

            # self.canvas.create_line(x[0], y[0], x[1], y[1], x[2], y[2], x[3], y[3], x[4], y[4], x[5], y[5], x[6], y[6],
            #                         x[7], y[7], x[8], y[8], smooth=True, fill='maroon2', arrow=LAST,
            #                         arrowshape=(9, 11, 4))
            for i in range(len(points) - 1):
                source = QPointF(points[i][0], points[i][1])
                dest = QPointF(points[i + 1][0], points[i + 1][1])
                line = QLineF(source, dest)
                qp.drawLine(line)
                if i == len(points) - 2:  # if this is the last line
                    # draw an arrow
                    self.create_arrow(qp, source.x(), source.y(), dest.x(), dest.y())


    def create_arrow(self, qp, x_1, y_1, x_2, y_2):
        """
        Used for the last part of a flow or a connector
        :param qp:
        :param x_1:
        :param y_1:
        :param x_2:
        :param y_2:
        :return:
        """
        source = QPointF(x_1, y_1)
        dest = QPointF(x_2, y_2)
        line = QLineF(source, dest)
        qp.drawLine(line)
        # draw an arrow
        v = line.unitVector()
        v.setLength(10)  # change the unit, => change the length of the arrow
        v.translate(QPointF(line.dx(), line.dy()))  # move it to the end of the line
        v2 = v.normalVector().normalVector()  # move backward along this line
        v.translate(v2.dx(), v2.dy())  # move v to the end of v2

        n = v.normalVector()  # normal vector
        n.setLength(n.length() * 0.5)  # width of the arrow
        n2 = n.normalVector().normalVector()  # an opposite vector of n

        p1 = v.p2()
        p2 = n.p2()
        p3 = n2.p2()
        qp.setBrush(QColor(0, 0, 0))
        qp.drawPolygon(p1, p2, p3)
        qp.setBrush(QColor(255, 255, 255))

    @staticmethod
    def cos_formula(a, b):
        l = 0
        m = 0
        n = 0
        for i in range(2):
            l += a[i] * b[i]
            m += a[i] ** 2
            n += b[i] ** 2
        return l / ((m * n) ** 0.5)

    def locate_alias(self, uid):
        # print("locate_alias is called, locating...")
        for element in self.sfd.nodes:
            if element == uid:
                x = self.sfd.nodes[element]['pos'][0]
                y = self.sfd.nodes[element]['pos'][1]
                return [float(x), float(y)]

    def draw_sfd_elements(self, qp):
        """
        A script of how should everything be drawn.
        :param qp: QPainter
        :return:
        """
        print("\nSFD Canvas is drawing...")
        # TODO need to rescale the window? scroll bars?
        # set common parameters
        width_stock = 45
        height_stock = 35
        radius1 = 8

        # draw stocks
        for element in self.sfd.nodes:
            if self.sfd.nodes[element]['element_type'] == STOCK:
                print("    SFD Canvas is drawing stock {}".format(element))
                x = self.sfd.nodes[element]['pos'][0]
                y = self.sfd.nodes[element]['pos'][1]
                # print(x,y)
                self.create_stock(qp, x, y, width_stock, height_stock, element)
                if x > self.xmost:
                    self.xmost = x
                if y > self.ymost:
                    self.ymost = y

        # draw flows
        for element in self.sfd.nodes:
            if self.sfd.nodes[element]['element_type'] == FLOW:
                print("    SFD Canvas is drawing flow {}".format(element))
                x = self.sfd.nodes[element]['pos'][0]
                y = self.sfd.nodes[element]['pos'][1]
                points = self.sfd.nodes[element]['points']
                self.create_flow(qp, x, y, points, radius1, element)
                if x > self.xmost:
                    self.xmost = x
                if y > self.ymost:
                    self.ymost = y

        # draw auxs
        for element in self.sfd.nodes:
            if self.sfd.nodes[element]['element_type'] in [PARAMETER, VARIABLE]:
                print("    SFD Canvas is drawing {} {}".format(self.sfd.nodes[element]['element_type'], element))
                x = self.sfd.nodes[element]['pos'][0]
                y = self.sfd.nodes[element]['pos'][1]
                self.create_aux(qp, x, y, radius1, element)
                if x > self.xmost:
                    self.xmost = x
                if y > self.ymost:
                    self.ymost = y

        for element in self.sfd.nodes:
            if self.sfd.nodes[element]['element_type'] == ALIAS:
                print("    SFD Canvas is drawing alias {}".format(element))
                x = self.sfd.nodes[element]['pos'][0]
                y = self.sfd.nodes[element]['pos'][1]
                of_element = self.sfd.nodes[element]['function']
                self.create_alias(qp, x, y, radius1, of_element)
                if x > self.xmost:
                    self.xmost = x
                if y > self.ymost:
                    self.ymost = y

        # draw connectors
        for connector in self.sfd.edges():
            from_element = connector[0]
            to_element = connector[1]
            if self.sfd[from_element][to_element]['display']:
                # Only draw when 'display' == True, avoid FLOW--->STOCK
                print('    SFD Canvas is drawing connector from {} to {}'.format(from_element, to_element))
                from_cord = self.locate_var(from_element)
                # print(from_cord)
                to_cord = self.locate_var(to_element)
                # print(to_cord)
                angle = self.sfd[from_element][to_element]['angle']
                # print('angle:', angle)
                self.create_connector(qp, from_cord[0], from_cord[1], to_cord[0], to_cord[1], angle)

        self.xmost += 150
        self.ymost += 100
        # print('Xmost,', self.xmost, 'Ymost,', self.ymost)

    def paintEvent(self, event):
        """
        This function is the 'draw everything' one, so another function (draw_sfd_elements) is then used as 'scripts'
        :param event:
        :return:
        """
        qp = QPainter()
        qp.begin(self)
        self.draw_sfd_elements(qp)
        qp.end()
