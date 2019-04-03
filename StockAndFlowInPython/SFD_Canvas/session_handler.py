import xml.dom.minidom
import math
from tkinter import filedialog
from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from StockAndFlowInPython.Graph_SD.graph_based_engine import Session, function_names, STOCK, FLOW, PARAMETER, VARIABLE, ALIAS
from StockAndFlowInPython.parsing.XMILE_parsing import parsing_equation
from StockAndFlowInPython.SFD_Canvas.SFD_Canvas import SFDCanvas


def name_handler(name):
    return name.replace(' ', '_').replace('\n', '_')


class SessionHandler(object):
    def __init__(self):
        # backends
        self.sess1 = Session()
        self.filename = ''
        self.model = None
        self.variables_in_model = None
        self.selected_variable = None

        # front ends
        self.sfd_window1 = SFDWindow()
        self.graph_network_window1 = GraphNetworkWindow()
        self.simulation_result1 = SimulationResult()


    def file_load(self):
        self.filename = filedialog.askopenfilename()
        if self.filename != '':
            self.read_xmile_model(self.filename)
            self.sfd_drawer()
            self.graph_network_drawer()
            self.variables_in_model = list(self.sess1.structures['default'].sfd.nodes)
            print(self.filename)
            return (self.filename, self.variables_in_model)

    def simulation_handler(self, simulation_time=80):
        self.sess1.simulate(simulation_time=simulation_time)

    def show_result(self):
        try:
            self.simulation_result1.canvas1.get_tk_widget().destroy()
        except:
            pass
        self.result_figure = self.sess1.draw_results(names=[self.selected_variable], rtn=True)
        self.simulation_result1.canvas1 = FigureCanvasTkAgg(self.result_figure, master=self.simulation_result1.top)
        self.simulation_result1.canvas1.get_tk_widget().pack(side=TOP)

    def add_angle_to_eqn(self, name, eqn):
        if eqn[0] in function_names:
            for factor in eqn[1:]:
                if type(factor[0]) == str:
                    factor[1] = self.get_angle(to_element=name, from_element=factor[0])
            return eqn
        else:
            return eqn

    def get_angle(self, from_element, to_element):
        for connection_view_array in self.connection_views_array:
            if connection_view_array[3] == to_element:
                if connection_view_array[2] == from_element:
                    return connection_view_array[1]

    def get_into_stock(self, flow_name):  # get the affected stock given a flow's name
        for stock_view_array in self.stock_views_array:
            if stock_view_array[2] == flow_name:
                return stock_view_array[0]
        return None

    def get_outfrom_stock(self, flow_name):  # get the affected stock given a flow's name
        for stock_view_array in self.stock_views_array:
            if stock_view_array[3] == flow_name:
                return stock_view_array[0]
        return None

    def read_xmile_model(self, filename):
        DOMTree = xml.dom.minidom.parse(filename)
        self.model = DOMTree.documentElement

        # fetch all variables in the file
        # since there is only one "variables" in the file, the outcome
        # is a list containing only one element of "variables"

        allvariables = self.model.getElementsByTagName("variables")

        # fetch all stocks/flows/aux/connectors in all variables (the only element in the list)

        self.stock_definitions = allvariables[0].getElementsByTagName("stock")
        self.flow_definitions = allvariables[0].getElementsByTagName("flow")
        self.aux_definitions = allvariables[0].getElementsByTagName("aux")

        # fetch all views in the file ---> down to the view

        self.all_views = self.model.getElementsByTagName("views")
        self.views = self.all_views[0].getElementsByTagName("view")

        # fetch views for all connectors and draw
        self.connectorviews = []
        for connectorview in self.views[0].getElementsByTagName("connector"):
            if connectorview.hasAttribute("uid"):
                self.connectorviews.append(connectorview)

        self.connection_views_array = list()
        for connectorview in self.connectorviews:
            uid = connectorview.getAttribute("uid")
            angle = float(connectorview.getAttribute("angle"))
            try:
                from_element = connectorview.getElementsByTagName("from")[0].getElementsByTagName("alias")[
                    0].getAttribute('uid')
            except:
                from_element = connectorview.getElementsByTagName("from")[0].childNodes[0].data
                from_element = name_handler(from_element)

            try:
                to_element = connectorview.getElementsByTagName("to")[0].getElementsByTagName("alias")[0].getAttribute(
                    'uid')
            except:
                to_element = connectorview.getElementsByTagName("to")[0].childNodes[0].data
                to_element = name_handler(to_element)

            # print("From and to", from_element, to_element)
            print('formatting connector', uid, angle, 'from:', from_element, 'to:', to_element)
            # self.sess1.add_connector(uid=uid, angle=angle, from_element=from_element, to_element=to_element)
            self.connection_views_array.append([uid, angle, from_element, to_element])

        # fetch views for all stocks and draw
        self.stockviews = []
        for stockview in self.views[0].getElementsByTagName("stock"):
            if stockview.hasAttribute("name"):
                self.stockviews.append(stockview)

        self.stock_views_array = list()
        for stockview in self.stockviews:
            name = stockview.getAttribute("name")
            name = name_handler(name)
            # print("Adding this stock:", name)
            inflow = None
            outflow = None
            for stock_definition in self.stock_definitions:  # Loop to find a particular stock
                if name_handler(stock_definition.getAttribute("name")) == name:
                    eqn = stock_definition.getElementsByTagName("eqn")[0].firstChild.data
                    try:
                        inflow = stock_definition.getElementsByTagName("inflow")[0].firstChild.data
                    except:
                        pass
                    try:
                        outflow = stock_definition.getElementsByTagName("outflow")[0].firstChild.data
                    except:
                        pass

            x = float(stockview.getAttribute("x"))
            y = float(stockview.getAttribute("y"))
            print('adding stock', name)
            self.sess1.add_stock(name=name, equation=self.add_angle_to_eqn(name=name, eqn=parsing_equation(eqn)), x=x, y=y)
            self.stock_views_array.append([name, eqn, inflow, outflow, x, y])

        # fetch views for all flows and draw
        self.flowviews = []
        for flowview in self.views[0].getElementsByTagName("flow"):
            if flowview.hasAttribute("name"):
                self.flowviews.append(flowview)

        for flowview in self.flowviews:
            name = flowview.getAttribute("name")
            name = name_handler(name)
            # print("Adding this flow:", name)
            for flow_definition in self.flow_definitions:  # loop to find a particular flow
                if name_handler(flow_definition.getAttribute("name")) == name:
                    eqn = flow_definition.getElementsByTagName("eqn")[0].firstChild.data
            points = list()
            for point in flowview.getElementsByTagName("pt"):
                points.append((point.getAttribute("x"), point.getAttribute("y")))
            x = float(flowview.getAttribute("x"))
            y = float(flowview.getAttribute("y"))
            print('adding flow', name)
            self.sess1.add_flow(name=name,
                                equation=self.add_angle_to_eqn(name=name, eqn=parsing_equation(eqn)),
                                x=x, y=y,
                                flow_from=self.get_outfrom_stock(name),
                                flow_to=self.get_into_stock(name),
                                points=points)

        # fetch views for all auxiliaries and draw
        self.auxviews = []
        for auxview in self.views[0].getElementsByTagName("aux"):
            if auxview.hasAttribute("name"):
                #print(auxview.getAttribute("name"), "heeeeeeeee")
                self.auxviews.append(auxview)

        for auxview in self.auxviews:
            name = auxview.getAttribute("name")
            name = name_handler(name)
            # print("Adding this aux:", name)
            for aux_definition in self.aux_definitions:  # Loop to find a particular aux
                if name_handler(aux_definition.getAttribute("name")) == name:
                    eqn = aux_definition.getElementsByTagName("eqn")[0].firstChild.data
            x = float(auxview.getAttribute("x"))
            y = float(auxview.getAttribute("y"))
            print('adding aux', name)
            self.sess1.add_aux(name=name, equation=self.add_angle_to_eqn(name=name, eqn=parsing_equation(eqn)), x=x, y=y)

        # fetch views for all aliases and draw
        self.aliasviews = []
        for aliasview in self.views[0].getElementsByTagName("alias"):
            # distinguish definition of alias from refering to it (cannot use 'color': sometimes there isn't)
            if aliasview.hasAttribute("x"):
                #print(aliasview.getAttribute("x"), "herererere!!")
                self.aliasviews.append(aliasview)

        for aliasview in self.aliasviews:
            uid = aliasview.getAttribute("uid")
            x = float(aliasview.getAttribute("x"))
            y = float(aliasview.getAttribute("y"))
            of = aliasview.getElementsByTagName("of")[0].firstChild.data
            # print('\n', uid, 'of', of, 'bbbbbbbb\n')
            of = name_handler(of)
            print('adding alias', name)
            self.sess1.add_alias(uid=uid, of_element=of, x=x, y=y)

        print('\nnodes: ', self.sess1.structures['default'].sfd.nodes)
        print('edges: ', self.sess1.structures['default'].sfd.edges)

        """Below is the function for drawing a SFD"""

    def create_stock(self, x, y, w, h, label):
        """
        Center x, Center y, width, height, label
        """
        self.sfd_window1.sfd_canvas1.canvas.create_rectangle(x - w * 0.5, y - h * 0.5, x + w * 0.5, y + h * 0.5, fill="#fff")
        self.sfd_window1.sfd_canvas1.canvas.create_text(x, y + 30, anchor=CENTER, font=("Arial", 10), text=label)

    def create_flow(self, x, y, pts, r, label):
        """
        Starting point x, y, ending point x, y, length, circle radius, label
        """
        for i in range(len(pts)-1):
            if i != len(pts)-2:
                self.sfd_window1.sfd_canvas1.canvas.create_line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1])
            else:
                self.sfd_window1.sfd_canvas1.canvas.create_line(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1], arrow=LAST)
        # self.canvas.create_line(xA, yA, xB, yB, arrow=LAST)
        self.sfd_window1.sfd_canvas1.canvas.create_oval(x - r, y - r, x + r, y + r, fill="#fff")
        self.sfd_window1.sfd_canvas1.canvas.create_text(x, y + r + 10, anchor=CENTER, font=("Arial", 10), text=label)

    def create_aux(self, x, y, r, label):
        """
        Central point x, y, radius, label
        """
        self.sfd_window1.sfd_canvas1.canvas.create_oval(x - r, y - r, x + r, y + r, fill="#fff")
        self.sfd_window1.sfd_canvas1.canvas.create_text(x, y + r + 10, anchor=CENTER, font=("Arial", 10), text=label)

    def create_alias(self, x, y, r, label):
        """
        Central point x, y, radius, label
        """
        self.sfd_window1.sfd_canvas1.canvas.create_oval(x - r, y - r, x + r, y + r, fill="gray70")
        self.sfd_window1.sfd_canvas1.canvas.create_text(x, y, anchor=CENTER, font=("Arial", 10), text="G")
        self.sfd_window1.sfd_canvas1.canvas.create_text(x, y + r + 10, anchor=CENTER, font=("Arial", 10, "italic"), text=label)

    def create_connector(self, xA, yA, xB, yB, angle, color='black'):
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
        if xB != xA:
            gAB = (yA - yB) / (xB - xA)  # y axis inversed, could be 'zero division'
        else:
            gAB = 99.99
        # print('gradiantAB, ', gAB)

        gM = (-1) / gAB
        # print('gradiantM, ', gM)
        xM = (xA + xB) / 2
        yM = (yA + yB) / 2
        # print("M's coordinate", xM, yM)

        xC = (yA + gA * xA - gM * xM - yM) / (gA - gM)
        yC = yA - gA * (xC - xA)
        # print("A's coordinate: ", xA, yA)
        # print("C's coordinate: ", xC, yC)

        # self.create_dot(xC, yC, 2, color, str(angle))  # draw center of the circle
        # TODO: when C and A are calculated to be the same point (and in fact not)
        rad_CA = math.atan2((yC - yA), (xA - xC))
        rad_CB = math.atan2((yC - yB), (xB - xC))

        # print('rad_CA, ', rad_CA, 'rad_CB, ', rad_CB)

        # calculate radius

        radius = (pow((xB - xC), 2) + pow((yC - yB), 2)) ** 0.5
        baseArc = math.atan2(yC - yA, xA - xC)

        # print('baseArc in degrees, ', math.degrees(baseArc))

        # print("checking youhu or liehu")
        # vectors, this part seems to be correct

        vecStarting = [math.cos(alpha), math.sin(alpha)]
        vecAtoB = [xB - xA, yA - yB]
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

        x = [xA]
        y = [yA]
        n = 7

        for i in range(n):
            baseArc = baseArc + diff / (n + 1) * inverse
            x1 = xC + radius * math.cos(baseArc)
            x.append(x1)
            y1 = yC - radius * math.sin(baseArc)
            y.append(y1)
            # Draw dots of the connectors, if you would like
            # self.create_dot(x1,y1,2,'gray',str(i))

        x.append(xB)
        y.append(yB)

        self.sfd_window1.sfd_canvas1.canvas.create_line(x[0], y[0], x[1], y[1], x[2], y[2], x[3], y[3], x[4], y[4], x[5], y[5], x[6], y[6],
                                x[7], y[7], x[8], y[8], smooth=True, fill='maroon2', arrow=LAST)

        # print('\n')

    def create_dot(self, x, y, r, color, label=''):
        self.sfd_window1.sfd_canvas1.canvas.create_oval(x - r, y - r, x + r, y + r, outline=color, fill=color)
        self.sfd_window1.sfd_canvas1.canvas.create_text(x, y - 10, anchor=CENTER, font=("Arial", 10), text=label)

    def cos_formula(self, a, b):

        l = 0
        m = 0
        n = 0
        for i in range(2):
            l += a[i] * b[i]
            m += a[i] ** 2
            n += b[i] ** 2
        return l / ((m * n) ** 0.5)

    def locate_var(self, name):
        name = name_handler(name)
        # print("locating...")
        # print(name)
        # print(self.session_handler1.sess1.structures['default'].sfd.nodes)
        for element in self.sess1.structures['default'].sfd.nodes:
            if element == name:
                x = self.sess1.structures['default'].sfd.nodes[element]['pos'][0]
                y = self.sess1.structures['default'].sfd.nodes[element]['pos'][1]
                return [float(x), float(y)]

    def locate_alias(self, uid):
        # print("locate_alias is called, locating...")
        for element in self.sess1.structures['default'].sfd.nodes:
            if element == uid:
                x = self.sess1.structures['default'].sfd.nodes[element]['pos'][0]
                y = self.sess1.structures['default'].sfd.nodes[element]['pos'][1]
                return [float(x), float(y)]

    def reset_canvas(self):
        self.sfd_window1.sfd_canvas1.canvas.delete('all')
        # self.lb.config(text='Load and display a Stella SD Model')
        # self.variables_in_model = ["Variable"]
        # self.comboxlist["values"] = self.variables_in_model
        # self.comboxlist.current(0)

        self.sess1.reset_a_structure()
        # TODO: rewrite matplotlib usages

        self.sfd_window1.sfd_canvas1.xmost = 300
        self.sfd_window1.sfd_canvas1.ymost = 300
        self.sfd_window1.sfd_canvas1.canvas.config(width=self.sfd_window1.sfd_canvas1.xmost, height=self.sfd_window1.sfd_canvas1.ymost, scrollregion=(0, 0, self.sfd_window1.sfd_canvas1.xmost, self.sfd_window1.sfd_canvas1.ymost))

    # Clear a simulation result but keep the structure
    def clear_a_run(self):
        self.sess1.clear_a_run()

    def file_handler(self, filename):
        DOMTree = xml.dom.minidom.parse(filename)
        # self.DOMTree = xml.dom.minidom.parse("./sample_models/reindeerModel.stmx")
        self.model = DOMTree.documentElement

    def sfd_drawer(self):
        # now starts the 'drawing' part
        self.sfd_window1.sfd_canvas1.canvas.config(width=self.sfd_window1.sfd_canvas1.xmost, height=self.sfd_window1.sfd_canvas1.ymost, scrollregion=(0, 0, self.sfd_window1.sfd_canvas1.xmost, self.sfd_window1.sfd_canvas1.ymost))

        # self.canvas.config(width = wid, height = hei)
        self.sfd_window1.sfd_canvas1.canvas.config(xscrollcommand=self.sfd_window1.sfd_canvas1.hbar.set, yscrollcommand=self.sfd_window1.sfd_canvas1.vbar.set)

        # set common parameters
        width1 = 46
        height1 = 35
        length1 = 115
        radius1 = 8

        for connector in self.sess1.structures['default'].sfd.edges():
            print('\n', connector)
            from_element = connector[0]
            to_element = connector[1]
            print('drawing connector from', from_element, 'to', to_element)
            from_cord = self.locate_var(from_element)
            # print(from_cord)
            to_cord = self.locate_var(to_element)
            # print(to_cord)
            angle = self.sess1.structures['default'].sfd[from_element][to_element][0]['angle']
            # print('angle:', angle)
            self.create_connector(from_cord[0], from_cord[1], to_cord[0], to_cord[1]-8, angle)

        # draw stocks
        for element in self.sess1.structures['default'].sfd.nodes:
            # print(element)
            # print(self.session_handler1.sess1.structures['default'].sfd.nodes.data())
            # print(self.session_handler1.sess1.structures['default'].sfd.nodes[element])
            # print("This element: ", element)
            # print("These elements:", self.session_handler1.sess1.structures['default'].sfd.nodes)
            if self.sess1.structures['default'].sfd.nodes[element]['element_type'] == STOCK:
                x = self.sess1.structures['default'].sfd.nodes[element]['pos'][0]
                y = self.sess1.structures['default'].sfd.nodes[element]['pos'][1]
                # print(x,y)
                self.create_stock(x, y, width1, height1, element)
                if x > self.sfd_window1.sfd_canvas1.xmost:
                    self.sfd_window1.sfd_canvas1.xmost = x
                if y > self.sfd_window1.sfd_canvas1.ymost:
                    self.sfd_window1.sfd_canvas1.ymost = y

        # draw flows
        for element in self.sess1.structures['default'].sfd.nodes:
            if self.sess1.structures['default'].sfd.nodes[element]['element_type'] == FLOW:
                x = self.sess1.structures['default'].sfd.nodes[element]['pos'][0]
                y = self.sess1.structures['default'].sfd.nodes[element]['pos'][1]
                points = self.sess1.structures['default'].sfd.nodes[element]['points']
                self.create_flow(x, y, points, radius1, element)
                if x > self.sfd_window1.sfd_canvas1.xmost:
                    self.sfd_window1.sfd_canvas1.xmost = x
                if y > self.sfd_window1.sfd_canvas1.ymost:
                    self.sfd_window1.sfd_canvas1.ymost = y

        # draw auxs
        for element in self.sess1.structures['default'].sfd.nodes:
            if self.sess1.structures['default'].sfd.nodes[element]['element_type'] in [PARAMETER, VARIABLE]:
                x = self.sess1.structures['default'].sfd.nodes[element]['pos'][0]
                y = self.sess1.structures['default'].sfd.nodes[element]['pos'][1]
                self.create_aux(x, y, radius1, element)
                if x > self.sfd_window1.sfd_canvas1.xmost:
                    self.sfd_window1.sfd_canvas1.xmost = x
                if y > self.sfd_window1.sfd_canvas1.ymost:
                    self.sfd_window1.sfd_canvas1.ymost = y

        for element in self.sess1.structures['default'].sfd.nodes:
            if self.sess1.structures['default'].sfd.nodes[element]['element_type'] == ALIAS:
                x = self.sess1.structures['default'].sfd.nodes[element]['pos'][0]
                y = self.sess1.structures['default'].sfd.nodes[element]['pos'][1]
                of_element = self.sess1.structures['default'].sfd.nodes[element]['function']
                self.create_alias(x, y, radius1, of_element)
                if x > self.sfd_window1.sfd_canvas1.xmost:
                    self.sfd_window1.sfd_canvas1.xmost = x
                if y > self.sfd_window1.sfd_canvas1.ymost:
                    self.sfd_window1.sfd_canvas1.ymost = y

        self.sfd_window1.sfd_canvas1.xmost += 150
        self.sfd_window1.sfd_canvas1.ymost += 100
        # print('Xmost,', self.xmost, 'Ymost,', self.ymost)
        self.sfd_window1.sfd_canvas1.canvas.config(width=self.sfd_window1.sfd_canvas1.xmost, height=self.sfd_window1.sfd_canvas1.ymost, scrollregion=(0, 0, self.sfd_window1.sfd_canvas1.xmost, self.sfd_window1.sfd_canvas1.ymost))
        self.sfd_window1.sfd_canvas1.canvas.pack(side=LEFT, expand=1, fill=BOTH)

        """Below is the function for drawing a SFD"""

    def graph_network_drawer(self):
        self.graph_network_window1.graph_figure = FigureCanvasTkAgg(self.sess1.draw_graphs(rtn=True), master=self.graph_network_window1.top)
        self.graph_network_window1.graph_figure._tkcanvas.pack(side=TOP)


class SFDWindow(object):
    def __init__(self):
        self.top = Toplevel()
        self.top.title("Stock and Flow Diagram")
        self.top.geometry("%dx%d+700+100" % (800, 500))
        self.sfd_canvas1 = SFDCanvas(self.top)


class GraphNetworkWindow(object):
    def __init__(self):
        self.top = Toplevel()
        self.top.title("Graph Network Structure")
        self.top.geometry("%dx%d+100+300" % (500, 500))


class SimulationResult(object):
    def __init__(self):
        self.top = Toplevel()
        self.top.title("Simulation Result")
        self.top.geometry("%dx%d+400+200" % (500, 500))
