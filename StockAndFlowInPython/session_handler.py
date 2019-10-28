import xml.dom.minidom
# import math
import time
import random
# import matplotlib.pyplot as plt
# import networkx as nx
# from grave import plot_network
# from tkinter import filedialog
# from tkinter import *
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from StockAndFlowInPython.graph_sd.graph_engine import Structure, function_names
from StockAndFlowInPython.parsing.XMILE_parsing import text_to_equation
# from StockAndFlowInPython.sfd_canvas.sfd_canvas_tkinter import SFDCanvas

SLEEP_TIME = 0


def name_handler(name):
    return name.replace(' ', '_').replace('\n', '_')


class SessionHandler(object):
    def __init__(self, model_structure=None):
        # backends
        if model_structure is None:
            self.model_structure = Structure()
        else:
            self.model_structure = model_structure
        self.filename = ''
        self.model = None
        self.variables_in_model = None
        self.selected_variable = None
        self.simulation_time = 75

    # def file_load(self):
    #     self.filename = filedialog.askopenfilename()
    #     if self.filename != '':
    #         self.read_xmile_model(self.filename)
    #         # draw sfd
    #         self.show_sfd_window()
    #         self.sfd_window1.sfd_canvas1.draw_existing_sfd(self.model_structure.sfd)
    #         # draw graph network
    #         self.draw_graph_network()
    #         self.variables_in_model = list(self.model_structure.sfd.nodes)
    #         print(self.filename)
    #         return (self.filename, self.variables_in_model)

    # def show_sfd_window(self):
    #     self.sfd_window1 = SFDWindow()

    # def show_graph_network_window(self):
    #     self.graph_network_window1 = GraphNetworkWindow()

    # def apply_generic_structure(self, generic_structure_type):
    #     """
    #     Retrieve a specific structure type by:
    #     1) Establish it in the graph engine;
    #     2) Draw SFD
    #     2) Draw Graph network
    #
    #     :param generic_structure_type:
    #     :return:
    #     """
    #     if generic_structure_type == 'decline_c':
    #         self.model_structure.first_order_negative()
    #     elif generic_structure_type == 'growth_b':
    #         self.model_structure.first_order_positive()
    #     # draw sfd
    #     self.sfd_window1 = SFDWindow()
    #     self.sfd_window1.sfd_canvas1.draw_existing_sfd(self.model_structure.sfd)
    #     # draw graph network
    #     self.draw_graph_network()
    #     self.variables_in_model = list(self.model_structure.sfd.nodes)

    def simulation_handler(self, simulation_time):
        self.model_structure.clear_a_run()
        self.model_structure.simulate(simulation_time=simulation_time)

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

    def get_into_stock(self, flow_name):
        """
        Get the affected stock given a flow's name
        :param flow_name:
        :return:
        """
        for stock_view_array in self.stock_views_array:
            if stock_view_array[2] == flow_name:
                return stock_view_array[0]
        return None

    def get_outfrom_stock(self, flow_name):
        """
        Get the affected stock given a flow's name
        :param flow_name:
        :return:
        """
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
            # self.model_structure.add_connector(uid=uid, angle=angle, from_element=from_element, to_element=to_element)
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
            eqn = None
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
            self.model_structure.add_stock(name=name,
                                           equation=self.add_angle_to_eqn(name=name, eqn=text_to_equation(eqn)),
                                           x=x,
                                           y=y)
            self.stock_views_array.append([name, eqn, inflow, outflow, x, y])

        # fetch views for all flows and draw
        self.flowviews = []
        for flowview in self.views[0].getElementsByTagName("flow"):
            if flowview.hasAttribute("name"):
                self.flowviews.append(flowview)

        for flowview in self.flowviews:
            name = flowview.getAttribute("name")
            name = name_handler(name)
            eqn = None
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
            self.model_structure.add_flow(name=name,
                                          equation=self.add_angle_to_eqn(name=name, eqn=text_to_equation(eqn)),
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
            eqn = None
            for aux_definition in self.aux_definitions:  # Loop to find a particular aux
                if name_handler(aux_definition.getAttribute("name")) == name:
                    eqn = aux_definition.getElementsByTagName("eqn")[0].firstChild.data
            x = float(auxview.getAttribute("x"))
            y = float(auxview.getAttribute("y"))
            print('adding aux', name)
            self.model_structure.add_aux(name=name, equation=self.add_angle_to_eqn(name=name, eqn=text_to_equation(eqn)), x=x, y=y)

        # fetch views for all aliases and draw
        self.aliasviews = []
        for aliasview in self.views[0].getElementsByTagName("alias"):
            # distinguish definition of alias from refering to it (cannot use 'color': sometimes there isn't)
            if aliasview.hasAttribute("x"):
                self.aliasviews.append(aliasview)

        for aliasview in self.aliasviews:
            uid = aliasview.getAttribute("uid")
            x = float(aliasview.getAttribute("x"))
            y = float(aliasview.getAttribute("y"))
            of = aliasview.getElementsByTagName("of")[0].firstChild.data
            of = name_handler(of)
            print('adding alias', of)
            self.model_structure.add_alias(uid=uid, of_element=of, x=x, y=y)

        print('\nnodes: ', self.model_structure.sfd.nodes)
        print('edges: ', self.model_structure.sfd.edges)

    def clear_a_run(self):
        """
        Clear a simulation result but keep the structure
        :return:
        """
        self.model_structure.clear_a_run()

    def file_handler(self, filename):
        DOMTree = xml.dom.minidom.parse(filename)
        # self.DOMTree = xml.dom.minidom.parse("./sample_models/reindeerModel.stmx")
        self.model = DOMTree.documentElement

    # def draw_graph_network(self):
    #     try:
    #         self.graph_network_window1.canvas1.get_tk_widget().destroy()  # clear graph network display
    #     except:
    #         pass
    #     self.show_graph_network_window()
    #     self.graph_network_window1.canvas1 = FigureCanvasTkAgg(self.model_structure.draw_graphs_with_curve(rtn=True), master=self.graph_network_window1.top)
    #     self.graph_network_window1.canvas1.get_tk_widget().pack(side=TOP)

    # def show_result(self):
    #     # try:
    #     #     self.simulation_result1.canvas1.get_tk_widget().destroy()  # clear simulation result display
    #     # except:
    #     #     pass
    #     self.simulation_result1 = SimulationResult()
    #     self.result_figure = self.model_structure.draw_results(names=[self.selected_variable], rtn=True)
    #     self.simulation_result1.canvas1 = FigureCanvasTkAgg(self.result_figure, master=self.simulation_result1.top)
    #     self.simulation_result1.canvas1.get_tk_widget().pack(side=TOP)

    # def reset(self):
    #     """
    #     Clear SFD canvas;
    #     Clear graph network display;
    #     Clear simulation results;
    #     :return:
    #     """
    #     self.sfd_window1.sfd_canvas1.reset_canvas()
    #     try:
    #         self.graph_network_window1.canvas1.get_tk_widget().destroy()  # clear graph network display
    #     except:
    #         pass
    #     try:
    #         self.simulation_result1.canvas1.get_tk_widget().destroy()  # clear simulation result display
    #     except:
    #         pass
    #     self.model_structure.clear_a_run()
    #     self.model_structure.reset_a_structure()

    def refresh(self):
        """
        Refresh 1) graph network window 2) SFD window 3) variable list
        """
        self.variables_in_model = list(self.model_structure.sfd.nodes)

    def build_stock(self, name=None, initial_value=None, x=0, y=0):
        print("===>Building stock: {}".format(name))
        if x == 0 or y == 0:  # if x or y not specified, automatically generate it.
            # TODO: fix this line
            pos = self.generate_location([])
            x = pos[0]
            y = pos[1]
            print("Generated position for {} at x = {}, y = {}.".format(name, x, y))
        uid = self.model_structure.add_stock(name=name, equation=[initial_value], x=x, y=y)
        # TODO: fix this line
        # self.refresh()
        time.sleep(SLEEP_TIME)
        return uid

    def build_flow(self, name=None, equation=None, x=0, y=0, points=None, flow_from=None, flow_to=None):
        if points is None:
            points = []
        print("===>Building flow: {}".format(name if name is not None else 'new'))

        linked_vars = list()  # collect linked variables for generating location
        if type(equation) is int or type(equation) is float:  # if equation is number, wrap it into []
            equation = [equation]
        else:
            for linked_var in equation[1:]:  # loop all parameters the function takes
                if type(linked_var) is list:  # it's a name+angle instead of a number
                    linked_vars.append(linked_var[0])  # confirm the name to 'linked_vars'
        print('    Building flow:', name, 'is linked to', linked_vars)

        if x == 0 or y == 0:  # if x or y not specified, automatically generate it.
            pos = self.generate_location(linked_vars)
            x = pos[0]
            y = pos[1]

            # However, because a flow is assumed to be horizontally aligned with its in/out stock, then
            # 1) if it is only linked to one stock, stock's y -> flow's y
            # 2) if it is linked to 2 stocks, flow -> right in between them

            if flow_from is not None and flow_to is not None:
                print("This flow influences 2 stocks")
                x1 = self.model_structure.get_coordinate(flow_from)[0]
                y1 = self.model_structure.get_coordinate(flow_from)[1]
                x2 = self.model_structure.get_coordinate(flow_to)[0]
                y2 = self.model_structure.get_coordinate(flow_to)[1]
                x = (x1 + x2)/2
                y = (y1 + y2)/2
                direction_x = (x2-x1)/abs(x2-x1)
                direction_y = (y2-y1)/abs(y2-y1)
                if abs(x2 - x1) > abs(y2 - y1):
                    points = [(x1+direction_x*23, y1), (x, y1), (x, y2), (x2-direction_x*23, y2)]
                else:
                    points = [(x1, y1+direction_y*18), (x1, y), (x2, y), (x2, y2-direction_y*18)]
            elif flow_from is not None:
                print("This flow flows from {}".format(flow_from))
                y = self.model_structure.get_coordinate(flow_from)[1]
                x = self.model_structure.get_coordinate(flow_from)[0] + 107
                points = [[x - 85.5, y], [x + 85.5, y]]
            elif flow_to is not None:
                print("This flow flows to {}".format(flow_to))
                y = self.model_structure.get_coordinate(flow_to)[1]
                x = self.model_structure.get_coordinate(flow_to)[0] - 107
                points = [[x - 85.5, y], [x + 85.5, y]]

            # Points need to be generated as well
            # calculating using: x=181, y=145, points=[(85, 145), (266.5, 145)]
            # points = [[x - 85.5, y], [x + 85.5, y]]

            print("Generated position for {} at x = {}, y = {}.".format(name, x, y))

        # if points are not specified but positions are:
        if len(points) == 0:
            pts_0 = [x-40, y]
            pts_1 = [x+40, y]
            points = [pts_0, pts_1]

        uid = self.model_structure.add_flow(name=name,
                                            equation=equation,
                                            flow_from=flow_from,
                                            flow_to=flow_to,
                                            x=x,
                                            y=y,
                                            points=points)
        self.refresh()
        time.sleep(SLEEP_TIME)
        return uid

    def build_aux(self, name=None, equation=None, x=0, y=0):
        uid: int  # a type hint
        print("===>Building aux: {}".format(name))

        linked_vars = list()  # collect linked variables for generating location
        if type(equation) is int or type(equation) is float:  # if equation is number, wrap it into []
            equation = [equation]
        else:
            for linked_var in equation[1:]:  # loop all parameters the function takes
                if type(linked_var) is list:  # it's a name instead of a number
                    linked_vars.append(linked_var[0])
        print('    Building aux:', name, 'is linked to', linked_vars)

        if x == 0 or y == 0:  # if x or y not specified, automatically generate it.
            pos = self.generate_location(linked_vars)
            x = pos[0]
            y = pos[1]
            print("Generated position for {} at x = {}, y = {}.".format(name, x, y))

        uid = self.model_structure.add_aux(name=name,
                                           equation=equation,
                                           x=x,
                                           y=y)
        self.refresh()
        time.sleep(SLEEP_TIME)
        return uid

    def build_connector(self, from_var, to_var, angle=None, polarity=None):
        self.model_structure.add_causality(from_element=from_var, angle=angle, to_element=to_var, polarity=polarity)

    def generate_location(self, linked_vars):
        """
        Automatically decide where to put a variable.
        :param linked_vars: A list of variables that are linked to this new var
        :return: A x-y coordinate for the new variable
        """
        # sfd_window.top.update()
        # canvas_width = sfd_window.top.winfo_width()
        # canvas_height = sfd_window.top.winfo_height()
        canvas_width = 640
        canvas_height = 480

        # When it is isolated: centered
        if len(linked_vars) == 0:
            print("Generating location. Isolated.")
            base_x = canvas_width / 2
            base_y = canvas_height / 2
            random_range = 50
            return random.randint(base_x - random_range, base_x + random_range), \
                   random.randint(base_y - random_range, base_y + random_range)
        # When it is linked to only one exiting variable: somewhere around it
        elif len(linked_vars) == 1:
            print("Generating location. Linked to one variable.")
            base_x = self.model_structure.get_coordinate(linked_vars[0])[0]
            base_y = self.model_structure.get_coordinate(linked_vars[0])[1]
            random_range = 65
            return random.randint(base_x - random_range, base_x + random_range), \
                   random.randint(base_y - random_range, base_y + random_range)
        # when it is linked to 2 or more variables: somewhere around the geometric center
        else:
            base_x = base_y = 0
            print("Generating location. Linked to {} variables.".format(len(linked_vars)))
            for linked_var in linked_vars:
                base_x += self.model_structure.get_coordinate(linked_var)[0]
                base_y += self.model_structure.get_coordinate(linked_var)[1]
            base_x = round(base_x / len(linked_vars))
            base_y = round(base_y / len(linked_vars))
            random_range = 80
            return random.randint(base_x - random_range, base_x + random_range), \
                   random.randint(base_y - random_range, base_y + random_range)

    def delete_variable(self, name):
        """
        Remove a variable from model structure
        :param name: Name of the variable
        :return:
        """
        self.model_structure.delete_element(name=name)
        self.refresh()
        time.sleep(SLEEP_TIME)

    # def wrap_equation(self, equation):
    #     """
    #     Check if the equation is a number; if so, wrap it into []
    #     :param equation:
    #     :return:
    #     """
    #     try:
    #         equation = float(equation)
    #     except ValueError:
    #         pass
    #     if type(equation) == int or type(equation) == float:  # if equation is number, wrap it into []
    #         equation = [equation]
    #     return equation

    def replace_equation(self, name, new_equation):
        """
        Equation replacement as a part of model expansion
        :param name: Variable's name
        :param new_equation: New equation for this variable
        :return:
        """
        # new_equation = self.wrap_equation(new_equation)
        self.model_structure.replace_equation(name, new_equation)
        self.refresh()

    def connect_stock_flow(self, flow_name, new_flow_from=None, new_flow_to=None):
        # step 1: remove connectors from this flow to those replaced
        # step 2: replace flow_from/flow_to by the new flow_from/to in the graph representation
        # step 3: confirm connectors according to the new flow_from/to
        if new_flow_from is not None:
            self.model_structure.create_stock_flow_connection(flow_name=flow_name, flow_from=new_flow_from)
            # Rearrange layout
            # pos
            self.model_structure.sfd.nodes[flow_name]['pos'][0] = self.model_structure.sfd.nodes[new_flow_from]['pos'][0] + 109
            self.model_structure.sfd.nodes[flow_name]['pos'][1] = self.model_structure.sfd.nodes[new_flow_from]['pos'][1]
            # points
            # left point
            self.model_structure.sfd.nodes[flow_name]['points'][0][0] = self.model_structure.sfd.nodes[flow_name]['pos'][0] - 85.5
            self.model_structure.sfd.nodes[flow_name]['points'][0][1] = self.model_structure.sfd.nodes[flow_name]['pos'][1]
            # right point
            self.model_structure.sfd.nodes[flow_name]['points'][1][0] = self.model_structure.sfd.nodes[flow_name]['pos'][0] + 85.5
            self.model_structure.sfd.nodes[flow_name]['points'][1][1] = self.model_structure.sfd.nodes[flow_name]['pos'][1]

        if new_flow_to is not None:
            self.model_structure.create_stock_flow_connection(flow_name=flow_name, flow_to=new_flow_to)
            # Rearrange layout
            # pos
            self.model_structure.sfd.nodes[flow_name]['pos'][0] = self.model_structure.sfd.nodes[new_flow_to]['pos'][0] - 109
            self.model_structure.sfd.nodes[flow_name]['pos'][1] = self.model_structure.sfd.nodes[new_flow_to]['pos'][1]
            # points
            # left point
            self.model_structure.sfd.nodes[flow_name]['points'][0][0] = self.model_structure.sfd.nodes[flow_name]['pos'][0] - 85.5
            self.model_structure.sfd.nodes[flow_name]['points'][0][1] = self.model_structure.sfd.nodes[flow_name]['pos'][1]
            # right point
            self.model_structure.sfd.nodes[flow_name]['points'][1][0] = self.model_structure.sfd.nodes[flow_name]['pos'][0] + 85.5
            self.model_structure.sfd.nodes[flow_name]['points'][1][1] = self.model_structure.sfd.nodes[flow_name]['pos'][1]

        self.refresh()

    def disconnect_stock_flow(self, flow_name, stock_name):
        """
        Disconnect stock and flow as a part of model expansion
        :param flow_name:
        :param stock_name:
        :return:
        """
        self.model_structure.remove_stock_flow_connection(flow_name, stock_name=stock_name)
        # Rearrange layout by 1) decide flow is on which side of the stock 2) increase the distance
        stock_x = self.model_structure.get_coordinate(stock_name)[0]
        flow_x = self.model_structure.get_coordinate(flow_name)[0]
        if stock_x >= flow_x:  # move flow leftward
            # pos
            self.model_structure.sfd.nodes[flow_name]['pos'][0] -= 20
            # points
            for i in range(len(self.model_structure.sfd.nodes[flow_name]['points'])):
                self.model_structure.sfd.nodes[flow_name]['points'][i][0] -= 20
        else:  # move flow rightward
            # pos
            self.model_structure.sfd.nodes[flow_name]['pos'][0] += 20
            # points
            for i in range(len(self.model_structure.sfd.nodes[flow_name]['points'])):
                self.model_structure.sfd.nodes[flow_name]['points'][i][0] += 20

        self.refresh()


# class SFDWindow(object):
#     def __init__(self):
#         self.top = Toplevel()
#         self.top.title("Stock and Flow Diagram")
#         self.top.geometry("%dx%d+1070+750" % (500, 430))
#         self.sfd_canvas1 = SFDCanvas(self.top)
#
#
# class GraphNetworkWindow(object):
#     def __init__(self):
#         self.top = Toplevel()
#         self.top.title("Graph Network Structure")
#         self.top.geometry("%dx%d+1070+50" % (500, 430))


# class NewGraphNetworkWindow(Toplevel):
#     def __init__(self, graph_network, window_title="Graph Network Structure", node_color="red",
#                  width=500, height=430, x=650, y=250, attr=None):
#         super().__init__()
#         self.title(window_title)
#         self.width = width
#         self.height = height
#         self.geometry("+{}+{}".format(x, y))
#         self.graph_network = graph_network
#         self.attr = attr
#         self.update_graph_network(node_color)
#
#     def update_graph_network(self, node_color):
#         try:
#             self.graph_network_canvas.get_tk_widget().destroy()
#         except :
#             pass
#         fig, ax = plt.subplots()
#
#         node_attr_mapping = nx.get_node_attributes(self.graph_network, self.attr)
#         for node, attr in node_attr_mapping.items():
#             node_attr_mapping[node] = "{} [{}]".format(node, attr)
#         nx.draw(self.graph_network,
#                 labels=node_attr_mapping,
#                 font_size=9,
#                 node_color=node_color,
#                 font_color='black',
#                 #with_labels=True
#                 )
#         self.graph_network_canvas = FigureCanvasTkAgg(figure=fig, master=self)
#         self.graph_network_canvas.get_tk_widget().configure(width=self.width, height=self.height)
#         self.graph_network_canvas.get_tk_widget().pack(side=LEFT)
#         self.update()

    # def update_graph_network_grave(self):
    #     try:
    #         self.graph_network_canvas.get_tk_widget().destroy()
    #     except :
    #         pass
    #     fig, ax = plt.subplots()
    #     art = plot_network(self.graph_network, ax=ax)
    #     self.graph_network_canvas = FigureCanvasTkAgg(figure=fig, master=self)
    #     self.graph_network_canvas.get_tk_widget().pack(side=LEFT)
    #     self.update()
    #
    # def highlighter(self, event):
    #     print("Triggered")


# class SimulationResult(object):
#     def __init__(self):
#         self.top = Toplevel()
#         self.top.title("Simulation Result")
#         self.top.geometry("%dx%d+560+50" % (500, 430))
