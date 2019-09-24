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
        pass

    def create_stock(self, qp, x, y, w, h, label):
        """
        Center x, Center y, width, height, label
        """
        qp.setBrush(QColor(255, 255, 255))
        qp.drawRect(x, y, w, h)
        qp.drawText(QRect(x-30, y+30, w+60, h),
                    Qt.AlignCenter,
                    label)

    def create_flow(self, qp, x, y, pts, r, label):
        pass

    def create_aux(self, qp, x, y, r, label):
        pass

    def create_alias(self, qp, x, y, r, label):
        pass

    def create_connector(self, qp, x_a, y_a, x_b, y_b, angle=None):
        pass

    def create_dot(self, qp, x, y, r, color, label=''):
        pass

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
        pass

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
