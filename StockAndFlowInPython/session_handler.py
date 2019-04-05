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
        self.simulation_time = 75

        # front ends
        self.sfd_window1 = None
        self.graph_network_window1 = None
        # self.simulation_result1 = SimulationResult()

    def file_load(self):
        self.filename = filedialog.askopenfilename()
        if self.filename != '':
            self.read_xmile_model(self.filename)
            # draw sfd
            self.sfd_window1 = SFDWindow()
            self.sfd_window1.sfd_canvas1.set_sfd_and_draw(self.sess1.structures['default'].sfd)
            # draw graph network
            self.draw_graph_network()
            self.variables_in_model = list(self.sess1.structures['default'].sfd.nodes)
            print(self.filename)
            return (self.filename, self.variables_in_model)

    def apply_generic_structure(self, generic_structure_type):
        if generic_structure_type == 'decline_c':
            self.sess1.first_order_negative()
        elif generic_structure_type == 'growth_b':
            self.sess1.first_order_positive()
        # draw sfd
        self.sfd_window1 = SFDWindow()
        self.sfd_window1.sfd_canvas1.set_sfd_and_draw(self.sess1.structures['default'].sfd)
        # draw graph network
        self.draw_graph_network()
        self.variables_in_model = list(self.sess1.structures['default'].sfd.nodes)

    def simulation_handler(self, simulation_time):
        self.sess1.clear_a_run()
        self.sess1.simulate(simulation_time=simulation_time)

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

    # Clear a simulation result but keep the structure
    def clear_a_run(self):
        self.sess1.clear_a_run()

    def file_handler(self, filename):
        DOMTree = xml.dom.minidom.parse(filename)
        # self.DOMTree = xml.dom.minidom.parse("./sample_models/reindeerModel.stmx")
        self.model = DOMTree.documentElement

    def draw_graph_network(self):
        try:
            self.graph_network_window1.canvas1.get_tk_widget().destroy()  # clear graph network display
        except:
            pass
        self.graph_network_window1 = GraphNetworkWindow()
        self.graph_network_window1.canvas1 = FigureCanvasTkAgg(self.sess1.draw_graphs_with_curve(rtn=True), master=self.graph_network_window1.top)
        self.graph_network_window1.canvas1.get_tk_widget().pack(side=TOP)

    def show_result(self):
        try:
            self.simulation_result1.canvas1.get_tk_widget().destroy()  # clear simulation result display
        except:
            pass
        self.simulation_result1 = SimulationResult()
        self.result_figure = self.sess1.draw_results(names=[self.selected_variable], rtn=True)
        self.simulation_result1.canvas1 = FigureCanvasTkAgg(self.result_figure, master=self.simulation_result1.top)
        self.simulation_result1.canvas1.get_tk_widget().pack(side=TOP)

    def reset(self):
        self.sfd_window1.sfd_canvas1.reset_canvas()
        try:
            self.graph_network_window1.canvas1.get_tk_widget().destroy()  # clear graph network display
        except:
            pass
        try:
            self.simulation_result1.canvas1.get_tk_widget().destroy()  # clear simulation result display
        except:
            pass
        self.sess1.clear_a_run()
        self.sess1.reset_a_structure()


class SFDWindow(object):
    def __init__(self):
        self.top = Toplevel()
        self.top.title("Stock and Flow Diagram")
        self.top.geometry("%dx%d+1070+550" % (500, 430))
        self.sfd_canvas1 = SFDCanvas(self.top)


class GraphNetworkWindow(object):
    def __init__(self):
        self.top = Toplevel()
        self.top.title("Graph Network Structure")
        self.top.geometry("%dx%d+1070+50" % (500, 430))


class SimulationResult(object):
    def __init__(self):
        self.top = Toplevel()
        self.top.title("Simulation Result")
        self.top.geometry("%dx%d+560+50" % (500, 430))
