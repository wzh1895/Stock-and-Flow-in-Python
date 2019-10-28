from tkinter import *
from StockAndFlowInPython.graph_sd.graph_engine import STOCK, FLOW, VARIABLE, PARAMETER, ALIAS
import math


class SFDCanvas(Frame):
    def __init__(self, master, width=900):
        super().__init__(master, width=width)
        self.master = master
        self.xmost = 300
        self.ymost = 300
        self.sfd = None

        self.canvas = Canvas(self)
        self.canvas.config(background='#fff')

        self.hbar = Scrollbar(self, orient=HORIZONTAL)
        self.hbar.pack(side=BOTTOM, fill=X)
        self.hbar.config(command=self.canvas.xview)

        self.vbar = Scrollbar(self, orient=VERTICAL)
        self.vbar.pack(side=RIGHT, fill=Y)
        self.vbar.config(command=self.canvas.yview)

        self.pack(fill=BOTH, expand=1)

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
        self.sfd_drawer()

    def reset_canvas(self):
        self.canvas.delete('all')
        # self.lb.config(text='Load and display a Stella SD Model')
        # self.variables_in_model = ["Variable"]
        # self.comboxlist["values"] = self.variables_in_model
        # self.comboxlist.current(0)

        # TODO: rewrite matplotlib usages

        self.xmost = 300
        self.ymost = 300
        self.canvas.config(width=self.xmost, height=self.ymost, scrollregion=(0, 0, self.xmost, self.ymost))

    def locate_var(self, name):
        for element in self.sfd.nodes:
            if element == name:
                x = self.sfd.nodes[element]['pos'][0]
                y = self.sfd.nodes[element]['pos'][1]
                return [float(x), float(y)]

        # if nothing is found (return is not triggered), try replace ' ' with '_'
        name = self.name_handler(name)

        for element in self.sfd.nodes:
            if element == name:
                x = self.sfd.nodes[element]['pos'][0]
                y = self.sfd.nodes[element]['pos'][1]
                return [float(x), float(y)]

    def create_stock(self, x, y, w, h, label):
        """
        Center x, Center y, width, height, label
        """
        self.canvas.create_rectangle(x - w * 0.5, y - h * 0.5, x + w * 0.5, y + h * 0.5, fill="#fff")
        self.canvas.create_text(x, y + 30, anchor=CENTER, font=("Arial", 10), text=label)

    def create_flow(self, x, y, pts, r, label):
        """
        Starting point x, y, ending point x, y, length, circle radius, label
        """
        for i in range(len(pts)-1):
            if i != len(pts)-2:
                self.canvas.create_line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1],
                                        arrow=LAST, arrowshape=(8, 10, 3))
            else:
                self.canvas.create_line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1],
                                        arrow=LAST, arrowshape=(8, 10, 3))
        # self.canvas.create_line(xA, yA, xB, yB, arrow=LAST)
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="#fff")
        self.canvas.create_text(x, y + r + 10, anchor=CENTER, font=("Arial", 10), text=label)

    def create_aux(self, x, y, r, label):
        """
        Central point x, y, radius, label
        """
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="#fff")
        self.canvas.create_text(x, y + r + 10, anchor=CENTER, font=("Arial", 10), text=label)

    def create_alias(self, x, y, r, label):
        """
        Central point x, y, radius, label
        """
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="gray70")
        self.canvas.create_text(x, y, anchor=CENTER, font=("Arial", 10), text="G")
        self.canvas.create_text(x, y + r + 10, anchor=CENTER, font=("Arial", 10, "italic"), text=label)

    def create_connector(self, x_a, y_a, x_b, y_b, angle=None, color='black'):
        if angle is None:
            self.canvas.create_line(x_a, y_a, x_b, y_b, smooth=True, fill='maroon2', arrow=LAST, arrowshape=(9, 11, 4))
        else:
            # self.create_dot(xA,yA,3,'black')
            # self.create_dot(xB,yB,3,'black')
            alpha = math.radians(angle)
            if math.pi < alpha < math.pi * 2:
                alpha -= math.pi * 2
            # beta = math.atan2((yA - yB), (xB - xA))  # angle between A->B and x-positive
            # print('alpha in degrees, ', math.degrees(alpha), 'beta in degrees, ', math.degrees(beta))

            # calculate the center of circle

            rad_radiusA = alpha - math.pi * 0.5  # radiant of radius of the circle going out from A
            # print('rad_radiusA (degrees), ', math.degrees(rad_radiusA), 'radians, ', rad_radiusA)
            gA = math.tan(rad_radiusA)
            # print('gradiantA, ', gA)
            if x_b != x_a:
                gAB = (y_a - y_b) / (x_b - x_a)  # y axis inversed, could be 'zero division'
            else:
                gAB = 99.99
            # print('gradiantAB, ', gAB)

            gM = (-1) / gAB
            # print('gradiantM, ', gM)
            xM = (x_a + x_b) / 2
            yM = (y_a + y_b) / 2
            # print("M's coordinate", xM, yM)

            xC = (y_a + gA * x_a - gM * xM - yM) / (gA - gM)
            yC = y_a - gA * (xC - x_a)
            # print("A's coordinate: ", xA, yA)
            # print("C's coordinate: ", xC, yC)

            # self.create_dot(xC, yC, 2, color, str(angle))  # draw center of the circle
            # TODO: when C and A are calculated to be the same point (and in fact not)
            rad_CA = math.atan2((yC - y_a), (x_a - xC))
            rad_CB = math.atan2((yC - y_b), (x_b - xC))

            # print('rad_CA, ', rad_CA, 'rad_CB, ', rad_CB)

            # calculate radius

            radius = (pow((x_b - xC), 2) + pow((yC - y_b), 2)) ** 0.5
            baseArc = math.atan2(yC - y_a, x_a - xC)

            # print('baseArc in degrees, ', math.degrees(baseArc))

            # print("checking youhu or liehu")
            # vectors, this part seems to be correct

            vecStarting = [math.cos(alpha), math.sin(alpha)]
            vecAtoB = [x_b - x_a, y_a - y_b]
            # print('vecStarting, ', vecStarting, 'vecAtoB, ', vecAtoB)
            angleCos = self.cos_formula(vecStarting, vecAtoB)
            # print('Cosine of the angle in Between, ', angleCos)

            # checking youhu or liehu the direction

            inverse = 1

            if angleCos < 0:  # you hu
                # print('deg_CA, ', math.degrees(rad_CA),'deg_CB',math.degrees(rad_CB))
                diff = rad_CB-rad_CA
                # print('youhu')
            else:  # lie hu
                if rad_CA*rad_CB<0 and rad_CA <= rad_CB: # yi hao
                    diff = rad_CB-rad_CA
                    if diff > math.pi:
                        diff = abs(diff) - math.pi*2
                elif rad_CA*rad_CB<0 and rad_CA > rad_CB:
                    diff = math.pi*2-rad_CA+rad_CB
                    if diff > math.pi:
                        diff = diff - math.pi*2
                elif rad_CA*rad_CB>0 and rad_CA > rad_CB:
                    diff = rad_CB-rad_CA
                    if diff > math.pi:
                        diff = math.pi*2 - diff
                elif rad_CA*rad_CB>0 and rad_CA < rad_CB:
                    diff = rad_CB-rad_CA
                    if diff > math.pi:
                        diff = math.pi*2 - diff
                else:
                    diff = rad_CB-rad_CA
                # print('liehu')
            # print('final diff in degrees, ', math.degrees(diff))
            # generate new points

            x = [x_a]
            y = [y_a]
            n = 7

            for i in range(n):
                baseArc = baseArc + diff / (n + 1) * inverse
                x1 = xC + radius * math.cos(baseArc)
                x.append(x1)
                y1 = yC - radius * math.sin(baseArc)
                y.append(y1)
                # Draw dots of the connectors, if you would like
                # self.create_dot(x1,y1,2,'gray',str(i))

            x.append(x_b)
            y.append(y_b)

            self.canvas.create_line(x[0], y[0], x[1], y[1], x[2], y[2], x[3], y[3], x[4], y[4], x[5], y[5], x[6], y[6],
                                    x[7], y[7], x[8], y[8], smooth=True, fill='maroon2', arrow=LAST, arrowshape=(9, 11, 4))

    def create_dot(self, x, y, r, color, label=''):
        self.canvas.create_oval(x - r, y - r, x + r, y + r, outline=color, fill=color)
        self.canvas.create_text(x, y - 10, anchor=CENTER, font=("Arial", 10), text=label)

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

    def sfd_drawer(self):
        # now starts the 'drawing' part
        print("\nSFD Canvas is drawing...")
        self.canvas.config(width=self.xmost, height=self.ymost, scrollregion=(0, 0, self.xmost, self.ymost))

        # self.canvas.config(width = wid, height = hei)
        self.canvas.config(xscrollcommand=self.hbar.set, yscrollcommand=self.vbar.set)

        # set common parameters
        width_stock = 45
        height_stock = 35
        length1 = 115
        radius1 = 8

        # draw stocks
        for element in self.sfd.nodes:
            if self.sfd.nodes[element]['element_type'] == STOCK:
                print("    SFD Canvas is drawing stock {}".format(element))
                x = self.sfd.nodes[element]['pos'][0]
                y = self.sfd.nodes[element]['pos'][1]
                # print(x,y)
                self.create_stock(x, y, width_stock, height_stock, element)
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
                self.create_flow(x, y, points, radius1, element)
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
                self.create_aux(x, y, radius1, element)
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
                self.create_alias(x, y, radius1, of_element)
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
                self.create_connector(from_cord[0], from_cord[1], to_cord[0], to_cord[1], angle)

        self.xmost += 150
        self.ymost += 100
        # print('Xmost,', self.xmost, 'Ymost,', self.ymost)
        self.canvas.config(width=self.xmost, height=self.ymost, scrollregion=(0, 0, self.xmost, self.ymost))
        self.canvas.pack(side=LEFT, expand=1, fill=BOTH)


# class GraphWindow():
#     def __init__(self, title, figure):
#         top = Toplevel()
#         top.title(title)
#         graph = FigureCanvasTkAgg(figure, master=top)
#         graph.draw()
#         graph._tkcanvas.pack()
