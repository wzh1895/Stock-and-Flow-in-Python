import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle
import numpy as np


# define constants
STOCK = 'stock'
FLOW = 'flow'
VARIABLE = 'variable'
PARAMETER = 'parameter'
CONNECTOR = 'connector'
ALIAS = 'alias'


# Define functions
class Functions(object):
    def __init__(self):
        pass

    @staticmethod
    def linear(x, a=1, b=0):
        return a * float(x) + b

    @staticmethod
    def addition(x, y):
        return float(x) + float(y)

    @staticmethod
    def subtract(x, y):
        return float(x) - float(y)

    @staticmethod
    def division(x, y):
        return float(x) / float(y)

    @staticmethod
    def multiplication(x, y):
        return float(x) * float(y)


LINEAR = Functions.linear
SUBTRACT = Functions.subtract
DIVISION = Functions.division
ADDITION = Functions.addition
MULTIPLICATION = Functions.multiplication

function_names = [LINEAR, SUBTRACT, DIVISION, ADDITION, MULTIPLICATION]


class UidManager(object):
    def __init__(self):
        self.uid = 0

    def get_new_uid(self):
        self.uid += 1
        return self.uid

    def current(self):
        return self.uid


class NameManager(object):
    def __init__(self):
        self.stock_id = 0
        self.flow_id = 0
        self.variable_id = 0
        self.parameter_id = 0

    def get_new_name(self, element_type):
        if element_type == STOCK:
            self.stock_id += 1
            return 'stock_'+str(self.stock_id)
        elif element_type == FLOW:
            self.flow_id += 1
            return 'flow_' + str(self.flow_id)
        elif element_type == VARIABLE:
            self.variable_id += 1
            return 'variable_' + str(self.variable_id)
        elif element_type == PARAMETER:
            self.parameter_id += 1
            return 'parameter_' + str(self.parameter_id)


class Structure(object):
    def __init__(self):
        self.sfd = nx.DiGraph()
        self.uid_manager = UidManager()
        self.name_manager = NameManager()
        self.uid_element_name = dict()
        self.simulation_time = None
        self.maximum_steps = 1000
        self.dt = 0.25

        self.set_predefined_structure = {'basic_stock_inflow': self.basic_stock_inflow,
                                         'basic_stock_outflow': self.basic_stock_outflow,
                                         'first_order_positive': self.first_order_positive,
                                         'first_order_negative': self.first_order_negative
                                         }

    def add_element(self, element_name, element_type, flow_from=None, flow_to=None, x=0, y=0, function=None, value=None, points=None):
        uid = self.uid_manager.get_new_uid()
        # this 'function' is a list, containing the function it self and its parameters
        # this 'value' is also a list, containing historical value throughout this simulation
        self.sfd.add_node(element_name, uid=uid, element_type=element_type, flow_from=flow_from, flow_to=flow_to, pos=[x, y], function=function, value=value, points=points)
        # print('Graph: adding element:', element_name, 'function:', function, 'value:', value)
        # automatically add dependencies, if a function is used for this variable
        if function is not None and type(function) is not str:
            self.add_function_dependencies(element_name, function)
        self.uid_element_name[uid] = element_name
        return uid

    def add_function_dependencies(self, element_name, function):  # add bunch of causality found in a function
        for from_variable in function[1:]:
            # print('Graph: adding causality, from_var:', from_variable)
            self.add_causality(from_element=from_variable[0], to_element=element_name, uid=self.uid_manager.get_new_uid(),
                               angle=from_variable[1])

    def add_causality(self, from_element, to_element, uid=0, angle=0, polarity=None, display=True):  # add one causality
        self.sfd.add_edge(from_element, to_element, uid=uid, angle=angle, polarity=polarity, display=display)  # display as a flag for to or not to display

    def get_element_by_uid(self, uid):
        return self.sfd.nodes[self.uid_element_name[uid]]

    def get_element_name_by_uid(self, uid):
        return self.uid_element_name[uid]

    def print_elements(self):
        print('Graph: All elements in this SFD:')
        print(self.sfd.nodes.data())

    def print_element(self, name):
        print('Graph: Attributes of element {}:'.format(name))
        print(self.sfd.nodes[name])

    def print_causalities(self):
        print('Graph: All causalities in this SFD:')
        print(self.sfd.edges)

    def print_causality(self, from_element, to_element):
        print('Graph: Causality from {} to {}:'.format(from_element, to_element))
        print(self.sfd[from_element][to_element])

    # TODO depreciate
    def all_stocks(self):
        stocks = list()
        for node, attributes in self.sfd.nodes.data():
            if attributes['element_type'] == STOCK:
                stocks.append(node)
        return stocks

    # TODO depreciate
    def all_flows(self):
        flows = list()
        for node, attributes in self.sfd.nodes.data():
            if attributes['element_type'] == FLOW:
                flows.append(node)
        return flows

    # TODO decpreciate
    def all_variables(self):
        variables = list()
        for node, attributes in self.sfd.nodes.data():
            if attributes['element_type'] == VARIABLE:
                variables.append(node)
        return variables

    # TODO decpreciate
    def all_parameters(self):
        parameters = list()
        for node, attributes in self.sfd.nodes.data():
            if attributes['element_type'] == PARAMETER:
                parameters.append(node)
        return parameters

    def all_certain_type(self, element_type):
        elements = list()
        for node, attributes in self.sfd.nodes.data():
            if attributes['element_type'] == element_type:
                elements.append(node)
        return elements

    def get_coordinate(self, name):
        """
        Get the coordinate of a specified variable
        :param name:
        :return: coordinate of the variable in a tuple
        """
        return self.sfd.nodes[name]['pos']

    def calculate(self, name):
        """
        Core function for simulation, based on recursion
        :param name: Name of the element to calculate
        """
        if self.sfd.nodes[name]['element_type'] == STOCK:
            # if the node is a stock
            return self.sfd.nodes[name]['value'][-1]  # just return its value, update afterward.
        elif self.sfd.nodes[name]['function'] is None:
            # if the node does not have a function and not a stock, then it's constant
            # if this node is a constant, still extend its value list by its last value
            self.sfd.nodes[name]['value'].append(self.sfd.nodes[name]['value'][-1])
            return self.sfd.nodes[name]['value'][-1]  # use its latest value
        else:  # it's not a constant value but a function  #
            # params = self.sfd.nodes[name]['function'][1:]  # extract all parameters needed by this function
            params = [param[0] for param in self.sfd.nodes[name]['function'][1:]]  # take the name but not the angle
            for j in range(len(params)):  # use recursion to find the values of params, then -
                params[j] = self.calculate(params[j])  # replace the param's name with its value.
            new_value = self.sfd.nodes[name]['function'][0](*params)  # calculate the new value for this step
            self.sfd.nodes[name]['value'].append(new_value)  # add this new value to this node's value list
            return new_value  # return the new value to where it was called

    def step(self, dt=0.25):
        """
        Core function for simulation. Calculating all flows and adjust stocks accordingly based on recursion.
        """
        flows_dt = dict()
        # have a dictionary of flows and their values in this dt, to be added to /subtracted from stocks afterward.

        # find all flows in the model
        for element in self.sfd.nodes:  # loop through all elements in this SFD,
            if self.sfd.nodes[element]['element_type'] == FLOW:  # if this element is a FLOW --
                flows_dt[element] = 0  # make a position for it in the dict of flows_dt, initializing it with 0

        # calculate flows
        for flow in flows_dt.keys():
            flows_dt[flow] = dt * self.calculate(flow)
        # print('All flows dt:', flows_dt)

        # calculating changes in stocks
        # have a dictionary of affected stocks and their changes, for one flow could affect 2 stocks.
        affected_stocks = dict()
        for flow in flows_dt.keys():
            successors = list(self.sfd.successors(flow))  # successors of a flow into a list
            # print('Successors of {}: '.format(flow), successors)
            for successor in successors:
                if self.sfd.nodes[successor]['element_type'] == STOCK:  # flow may also affect elements other than stock
                    direction_factor = 1  # initialize
                    if successor not in affected_stocks.keys():  # if this flow hasn't been calculated, create a new key
                        if self.sfd.nodes[flow]['flow_from'] == successor:  # if flow influences this stock negatively
                            direction_factor = -1
                        elif self.sfd.nodes[flow]['flow_to'] == successor:  # if flow influences this stock positively
                            direction_factor = 1
                        else:
                            print("Graph: Strange! {} seems to influence {} but not found in graph's attributes.".format(flow, successor))
                        affected_stocks[successor] = flows_dt[flow] * direction_factor
                    else:  # otherwise update this flow's value on top of results of previous calculation (f2 = f1 + f0)
                        if self.sfd.nodes[flow]['flow_from'] == successor:  # if flow influences this stock negatively
                            direction_factor = -1
                        elif self.sfd.nodes[flow]['flow_to'] == successor:  # if flow influences this stock positively
                            direction_factor = 1
                        else:
                            print("Graph: Strange! {} seems to influence {} but not found in graph's attributes.".format(flow, successor))
                        affected_stocks[successor] = flows_dt[flow] * direction_factor
                        affected_stocks[successor] += flows_dt[flow] * direction_factor

        # updating affected stocks values
        for stock in affected_stocks.keys():
            # calculate the new value for this stock and add it to the end of its value list
            self.sfd.nodes[stock]['value'].append(self.sfd.nodes[stock]['value'][-1] + affected_stocks[stock])
            # print('Stock ', stock, ': {:.4f}'.format(self.sfd.nodes[stock]['value'][-1]))

        # for those stocks not affected, extend its 'values' by the same value as it is
        for node in self.sfd.nodes:
            if self.sfd.nodes[node]['element_type'] == STOCK:
                if node not in affected_stocks.keys():
                    self.sfd.nodes[node]['value'].append(self.sfd.nodes[node]['value'][-1])
                    # print('Stock ', node, ': {:.4f}'.format(self.sfd.nodes[node]['value'][-1]))

    def clear_value(self):
        """
        Clear values for all nodes
        :return:
        """
        for node in self.sfd.nodes:
            if self.sfd.nodes[node]['element_type'] == STOCK:
                self.sfd.nodes[node]['value'] = [self.sfd.nodes[node]['value'][0]]  # for stock, keep its initial value
            else:
                if self.sfd.nodes[node]['function'] is None:  # it's a constant parameter
                    self.sfd.nodes[node]['value'] = [self.sfd.nodes[node]['value'][0]]
                else:  # it's not a constant parameter
                    self.sfd.nodes[node]['value'] = list()  # for other variables, reset its value to empty list
            # print('Graph: reset value of', node, 'to', self.sfd.nodes[node]['value'])

    # Add elements on a stock-and-flow level (work with model file handlers)
    def add_stock(self, name=None, equation=None, x=0, y=0):
        uid = self.add_element(name, element_type=STOCK, x=x, y=y, value=equation)
        # print('Graph: added stock:', name, 'to graph.')
        return uid

    def add_flow(self, name=None, equation=None, x=0, y=0, points=None, flow_from=None, flow_to=None):
        # Decide if the 'equation' is a function or a constant number
        if type(equation[0]) is int or type(equation[0]) is float:
            # if equation starts with a number
            function = None
            value = equation  # it's a constant
        else:
            function = equation  # it's a function
            value = list()
        if name is None:
            name = self.name_manager.get_new_name(element_type=FLOW)
        uid = self.add_element(name, element_type=FLOW, flow_from=flow_from, flow_to=flow_to, x=x, y=y, function=function, value=value, points=points)
        self.create_stock_flow_connection(name, flow_from=flow_from, flow_to=flow_to)
        # print('Graph: added flow:', name, 'to graph.')
        return uid

    def create_stock_flow_connection(self, name=None, flow_from=None, flow_to=None):
        """
        Connect stock and flow.
        :param name: The flow's name
        :param structure_name: The structure to modify
        :param flow_from: The stock this flow coming from
        :param flow_to: The stock this flow going into
        :return:
        """
        # If the flow influences a stock, create the causal link
        if flow_from is not None:  # Just set up
            self.sfd.nodes[name]['flow_from'] = flow_from
            self.add_causality(name, flow_from, display=False, polarity='negative')
        if flow_to is not None:  # Just set up
            self.sfd.nodes[name]['flow_to'] = flow_to
            self.add_causality(name, flow_to, display=False, polarity='positive')

    def add_aux(self, name=None, equation=None, x=0, y=0):
        # Decide if this aux is a parameter or variable
        if type(equation[0]) is int or type(equation[0]) is float:
            # if equation starts with a number, it's a parameter
            uid = self.add_element(name, element_type=PARAMETER, x=x, y=y, function=None, value=equation)
        else:
            # It's a variable, has its own function
            uid = self.add_element(name, element_type=VARIABLE, x=x, y=y, function=equation, value=list())
            # Then it is assumed to take information from other variables, therefore causal links should be created.
            # Already implemented in structure's add_element function, not needed here.
            # for info_source_var in equation[1]:
            #     if info_source_var in self.structures[structure_name].sfd.nodes:  # if this info_source is a var
            #         self.structures[structure_name].add_causality(info_source_var, name)
        # print('Graph: added aux', name, 'to graph.')
        return uid

    def replace_equation(self, name, new_equation):
        """
        Replace the equation of a variable.
        :param name: The name of the variable
        :param new_equation: The new equation
        :param structure_name: The structure the variable is in
        :return:
        """
        # step 1: remove all incoming connectors into this variable (node)
        # step 2: replace the equation of this variable in the graph representation
        # step 3: add connectors based on the new equation (only when the new equation is a function instead of a number
        print("Graph: Replacing equation of {}".format(name))
        # step 1:
        to_remove = list()
        for u, v in self.sfd.in_edges(name):
            print(u, v)
            to_remove.append((u, v))
        self.sfd.remove_edges_from(to_remove)
        print("Graph: Edges removed.")
        # step 2:
        if type(new_equation[0]) is int or type(new_equation[0]) is float:
            # If equation starts with a number, it's a constant value
            self.sfd.nodes[name]['function'] = None
            self.sfd.nodes[name]['value'] = new_equation
            print("Graph: Equation replaced.")
        else:
            # It's a variable, has its own function
            self.sfd.nodes[name]['function'] = new_equation
            self.sfd.nodes[name]['value'] = list()
            print("Graph: Equation replaced.")
            # step 3:
            if new_equation is not None and type(new_equation) is not str:
                self.add_function_dependencies(name, new_equation)
                print("Graph: New edges created.")

    # Add elements to a structure in a batch (something like a script)
    # Enable using of multi-dimensional arrays.
    def add_elements_batch(self, elements):
        for element in elements:
            if element[0] == STOCK:
                self.add_stock(name=element[1],
                               equation=element[2],
                               x=element[5],
                               y=element[6],)
            elif element[0] == FLOW:
                self.add_flow(name=element[1],
                              equation=element[2],
                              flow_from=element[3],
                              flow_to=element[4],
                              x=element[5],
                              y=element[6],
                              points=element[7])
            elif element[0] == PARAMETER or element[0] == VARIABLE:
                self.add_aux(name=element[1],
                             equation=element[2],
                             x=element[5],
                             y=element[6])
            elif element[0] == CONNECTOR:
                self.add_connector(uid=element[1],
                                   angle=element[2],
                                   from_element=element[3],
                                   to_element=element[4])

    def add_connector(self, uid, from_element, to_element, angle=0):
        self.add_causality(from_element, to_element, uid=uid, angle=angle)

    def add_alias(self, uid, of_element, x=0, y=0):
        self.add_element(uid, element_type=ALIAS, x=x, y=y, function=of_element)
        # print('Graph: added alias of', of_element, 'to graph.\n')

    def delete_variable(self, name):
        """
        Delete a variable
        :param name:
        :param structure_name:
        :return:
        """
        self.sfd.remove_node(name)
        print("Graph: {} is removed from the graph.".format(name))

    def remove_stock_flow_connection(self, name, stock_name):
        """
        Disconnect stock and flow
        :param name: The flow's name
        :param structure_name: The structure to modify
        :param stock_name: The stock this flow no longer connected to
        :return:
        """
        if self.sfd.nodes[name]['flow_from'] == stock_name:
            self.sfd.remove_edge(name, stock_name)
            self.sfd.nodes[name]['flow_from'] = None
        if self.sfd.nodes[name]['flow_to'] == stock_name:
            self.sfd.remove_edge(name, stock_name)
            self.sfd.nodes[name]['flow_to'] = None

        # # Set the previous 'from' to None, and remove the causal link if it exists
        # if self.structures[structure_name].sfd.nodes[name]['flow_from'] is not None:
        #     self.structures[structure_name].sfd.remove_edge(name, self.structures[structure_name].sfd.nodes[name]['flow_from'])
        #     self.structures[structure_name].sfd.nodes[name]['flow_from'] = None
        # # Set the previous 'to' to None, and remove the causal link if it exists
        # if self.structures[structure_name].sfd.nodes[name]['flow_from'] is not None:
        #     self.structures[structure_name].sfd.remove_edge(name, self.structures[structure_name].sfd.nodes[name]['flow_from'])
        #     self.structures[structure_name].sfd.nodes[name]['flow_from'] = None

    # Set the model to a first order negative feedback loop
    def first_order_negative(self):
        # adding a structure that has been pre-defined using multi-dimensional arrays.
        self.sfd.graph['structure_name'] = 'first_order_negative'
        self.add_elements_batch([
            # 0type,    1name/uid,  2value/equation/angle                         3flow_from,      4flow_to,        5x,     6y,     7pts,
            [STOCK,     'stock0',   [100],                                        None,       None,       289,    145,    None],
            [FLOW,      'flow0',    [DIVISION, ['gap0', 148], ['at0', 311]],      None,       'stock0',   181,    145,    [[85, 145], [266.5, 145]]],
            [PARAMETER, 'goal0',    [20],                                         None,       None,       163,    251,    None],
            [VARIABLE,  'gap0',     [SUBTRACT, ['goal0', 353], ['stock0', 246]],  None,       None,       213,    212,    None],
            [PARAMETER, 'at0',      [5],                                          None,       None,       123,    77,    None],
            # [CONNECTOR, '0',        246,                           'stock0',   'gap0',      0,      0,      None],
            # [CONNECTOR, '1',        353,                           'goal0',    'gap0',      0,      0,      None],
            # [CONNECTOR, '2',        148,                           'gap0',     'flow0',     0,      0,      None],
            # [CONNECTOR, '3',        311,                           'at0',      'flow0',     0,      0,      None]
            ])

    # Set the model to a first order negative feedback loop
    def first_order_positive(self):
        # adding a structure that has been pre-defined using multi-dimensional arrays.
        self.sfd.graph['structure_name'] = 'first_order_positive'
        self.add_elements_batch([
            # 0type,    1name/uid,   2value/equation/angle                                   3flow_from,      4flow_to,        5x,     6y,     7pts,
            [STOCK,     'stock0',    [1],                                                    None,       None,       289,    145,    None],
            [FLOW,      'flow0',     [MULTIPLICATION, ['stock0', 100], ['fraction0', 160]],  None,       'stock0',   181,    145,    [[85, 145], [266.5, 145]]],
            [PARAMETER, 'fraction0', [0.1],                                                  None,       None,       163,    251,    None],
        ])

    # Set the model to one stock + one outflow
    def basic_stock_outflow(self):
        self.sfd.graph['structure_name'] = 'basic_stock_outflow'
        self.add_elements_batch([
            # 0type,    1name/uid,   2value/equation/angle                                   3flow_from,      4flow_to,        5x,     6y,     7pts,
            [STOCK,     'stock0',    [100],                                                    None,       None,       289,    145,    None],
            [FLOW,      'flow0',     [4],                                                    'stock0',   None,       181,    145,    [[85, 145], [266.5, 145]]],
        ])

    # Set the model to one stock + one outflow
    def basic_stock_inflow(self):
        self.sfd.graph['structure_name'] = 'basic_stock_inflow'
        self.add_elements_batch([
            # 0type,    1name/uid,   2value/equation/angle                                   3flow_from,      4flow_to,        5x,     6y,     7pts,
            [STOCK,     'stock0',    [1],                                                    None,            None,            289,    145,    None],
            [FLOW,      'flow0',     [4],                                                    None,            'stock0',        181,    145, [[85, 145], [266.5, 145]]],
        ])

    # Clear a run
    def clear_a_run(self):
        self.clear_value()

    # Reset a structure
    def reset_a_structure(self):
        self.sfd.clear()

    # Simulate a structure based on a certain set of parameters
    def simulate(self, simulation_time, dt=0.25):
        # print('Graph: Simulating...')
        self.simulation_time = simulation_time
        self.dt = dt
        if simulation_time == 0:
            # determine how many steps to run; if not specified, use maximum steps
            total_steps = self.maximum_steps
        else:
            total_steps = int(simulation_time/dt)

        # main iteration
        for i in range(total_steps):
            # stock_behavior.append(structure0.sfd.nodes['stock0']['value'])
            # print('Step: {} '.format(i), end=' ')
            self.step(dt)

    # Return a behavior
    def get_behavior(self, name):
        # print(self.structures[structure_name].sfd.nodes[name]['value'])
        return self.sfd.nodes[name]['value']

    # Draw results
    def draw_results(self, names=None, rtn=False):
        if names is None:
            names = list(self.sfd.nodes)

        self.figure1 = plt.figure(figsize=(5, 5))

        # plt.subplot(212)  # operate subplot 2
        plt.xlabel('Steps (Time: {} / Dt: {})'.format(self.simulation_time, self.dt))
        plt.ylabel('Behavior')
        y_axis_minimum = 0
        y_axis_maximum = 0
        for name in names:
            # print("Graph: getting min/max for", name)
            # set the range of axis based on this element's behavior
            # 0 -> end of period (time), 0 -> 100 (y range)

            name_minimum = min(self.sfd.nodes[name]['value'])
            name_maximum = max(self.sfd.nodes[name]['value'])
            if name_minimum == name_maximum:
                name_minimum *= 2
                name_maximum *= 2
                # print('Graph: Centered this straight line')

            if name_minimum < y_axis_minimum:
                y_axis_minimum = name_minimum

            if name_maximum > y_axis_maximum:
                y_axis_maximum = name_maximum

            # print("Graph: Y range: ", y_axis_minimum, '-', y_axis_maximum)
            plt.axis([0, self.simulation_time/self.dt, y_axis_minimum, y_axis_maximum])
            t_series = self.sfd.nodes[name]['value']
            # print("Graph: Time series of {}:".format(name))
            # for i in range(len(t_series)):
            #     print("Graph: {0} at DT {1} : {2:8.4f}".format(name, i+1, t_series[i]))
            plt.plot(t_series, label=name)
        plt.legend()
        if rtn:  # if called from external, return the figure without show it.
            return self.figure1
        else:  # otherwise, show the figure.
            plt.show()

    # Draw graphs
    def draw_graphs(self, rtn=False):
        self.figure1 = plt.figure(figsize=(5, 5))
        plt.gca().invert_yaxis()  # invert y-axis to move the origin to upper-left point, matching tkinter's canvas
        pos = nx.get_node_attributes(self.sfd, 'pos')
        nx.draw(self.sfd, with_labels=True, pos=pos)

        if rtn:  # if called from external, return the figure without show it.
            return self.figure1
        else:  # otherwise, show the figure.
            plt.show()

    # Draw graphs with curve
    def draw_graphs_with_curve(self, rtn=False):
        self.figure1 = plt.figure(figsize=(8, 6))
        ax = plt.gca()
        ax.invert_yaxis()  # invert y-axis to move the origin to upper-left point, matching tkinter's canvas

        # disable all frames/borders
        ax.axes.get_yaxis().set_visible(False)
        ax.axes.get_xaxis().set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        pos = nx.get_node_attributes(self.sfd, 'pos')
        # print("Graph: The graph contains elements with their positions:", pos)
        self.draw_network(self.sfd, pos, ax)
        ax.autoscale()

        if rtn:  # if figure needs to be returned
            # print('Graph: Engine is returning graph figure.')
            return self.figure1
        else:
            plt.show()

    # Draw network with FancyArrowPatch
    # Thanks to https://groups.google.com/d/msg/networkx-discuss/FwYk0ixLDuY/dtNnJcOAcugJ
    def draw_network(self, G, pos, ax):
        for n in G:
            # print('Graph: Engine is drawing network element for', n)
            circle = Circle(pos[n], radius=5, alpha=0.2, color='c')
            # ax.add_patch(circle)
            G.node[n]['patch'] = circle
            x, y = pos[n]
            ax.text(x, y, n, fontsize=11, horizontalalignment='left', verticalalignment='center')
        seen = {}
        # TODO: Undertsand what happens here and rewrite it in a straight forward way
        if len(list(G.edges)) != 0:  # when there's only one stock in the model, don't draw edges
            for (u, v, d) in G.edges(data=True):
                n1 = G.node[u]['patch']
                n2 = G.node[v]['patch']
                rad = - 0.5
                if (u, v) in seen:
                    rad = seen.get((u, v))
                    rad = (rad + np.sign(rad)*0.1)*-1
                alpha = 0.5
                color = 'r'

                edge = FancyArrowPatch(n1.center, n2.center, patchA=n1, patchB=n2,
                                    arrowstyle='-|>',
                                    connectionstyle='arc3,rad=%s' % rad,
                                    mutation_scale=15.0,
                                    linewidth=1,
                                    alpha=alpha,
                                    color=color)
                seen[(u, v)] = rad
                ax.add_patch(edge)
            return edge


def main():
    structure0 = Structure()
    structure0.first_order_negative()
    structure0.simulate(simulation_time=80)
    structure0.draw_graphs_with_curve()
    structure0.all_stocks()


if __name__ == '__main__':
    main()
