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


class Structure(object):
    def __init__(self):
        self.sfd = nx.MultiDiGraph()
        self.uid = 0

    def uid_getter(self):
        self.uid += 1
        return self.uid

    def add_element(self, element_name, element_type, x=0, y=0, function=None, value=None, points=None):
        # this 'function' is a list, containing the function it self and its parameters
        # this 'value' is also a list, containing historical value throughout this simulation
        self.sfd.add_node(element_name, element_type=element_type, pos=(x, y), function=function, value=value, points=points)
        print('adding element:', element_name, 'function:', function, 'value:', value)
        # automatically add dependencies, if a function is used for this variable
        if function is not None and type(function) is not str:
            for from_variable in function[1:]:
                print('adding causality, from_var:', from_variable)
                self.add_causality(from_element=from_variable[0], to_element=element_name, uid=self.uid_getter(), angle=from_variable[1])

    def add_causality(self, from_element, to_element, uid=0, angle=0):
        self.sfd.add_edge(from_element, to_element, uid=uid, angle=angle)

    # def add_angle(self, from_element, to_element, uid=0, angle=0):

    def print_elements(self):
        print('All elements in this SFD:')
        print(self.sfd.nodes.data())

    def print_element(self, name):
        print('Attributes of element {}:'.format(name))
        print(self.sfd.nodes[name])

    def print_causalities(self):
        print('All causalities in this SFD:')
        print(self.sfd.edges)

    def print_causality(self, from_element, to_element):
        print('Causality from {} to {}:'.format(from_element, to_element))
        print(self.sfd[from_element][to_element])

    def get_coordinate(self, name):
        """
        Get the coordinate of a specified variable
        :param name:
        :return: coordinate of the variable in a tuple
        """
        return self.sfd.nodes[name]['pos']

    # The core function for simulation, based on recursion
    def calculate(self, name):
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
        flows_dt = dict()  # have a dictionary of flows and their values in this dt, to be added to stocks afterward.

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
                    if successor not in affected_stocks.keys():  # if this flow hasn't been calculated, create a new key
                        affected_stocks[successor] = flows_dt[flow]
                    else:  # otherwise update this flow's value on top of results of previous calculation (f2 = f1 + f0)
                        affected_stocks[successor] += flows_dt[flow]

        # updating affected stocks values
        for stock in affected_stocks.keys():
            # calculate the new value for this stock and add it to the end of its value list
            self.sfd.nodes[stock]['value'].append(self.sfd.nodes[stock]['value'][-1] + affected_stocks[stock])
            print('Stock ', stock, ':', self.sfd.nodes[stock]['value'][-1])

        # for those stocks not affected, extend its 'values' by the same value as it is
        for node in self.sfd.nodes:
            if self.sfd.nodes[node]['element_type'] == STOCK:
                if node not in affected_stocks.keys():
                    self.sfd.nodes[node]['value'].append(self.sfd.nodes[node]['value'][-1])
                    print('Stock ', node, ':', self.sfd.nodes[node]['value'][-1])

    def clear_value(self):
        # clear 'value' for all nodes
        for node in self.sfd.nodes:
            if self.sfd.nodes[node]['element_type'] == STOCK:
                self.sfd.nodes[node]['value'] = [self.sfd.nodes[node]['value'][0]]  # for stock, keep its initial value
            else:
                if self.sfd.nodes[node]['function'] is None:  # it's a constant parameter
                    self.sfd.nodes[node]['value'] = [self.sfd.nodes[node]['value'][0]]
                else:  # it's not a constant parameter
                    self.sfd.nodes[node]['value'] = list()  # for other variables, reset its value to empty list
            print('reset value of', node, 'to', self.sfd.nodes[node]['value'])


class Session(object):
    def __init__(self):
        self.simulation_time = None
        self.dt = 0.25
        self.structures = dict()
        self.add_structure()  # Automatically add a default structure

    def add_structure(self, structure_name='default'):
        self.structures[structure_name] = Structure()

    # Set the model to a first order negative feedback loop
    def first_order_negative(self, structure_name='default'):
        # adding a structure that has been pre-defined using multi-dimensional arrays.
        self.add_elements_batch([
            # 0type,    1name/uid,  2value/equation/angle                         3from,      4to,        5x,     6y,     7pts,
            [STOCK,     'stock0',   [100],                                        None,       None,       289,    145,    None],
            [FLOW,      'flow0',    [DIVISION, ['gap0', 148], ['at0', 311]],      None,       'stock0',   181,    145,    [(85, 145), (266.5, 145)]],
            [PARAMETER, 'goal0',    [20],                                         None,       None,       163,    251,    None],
            [VARIABLE,  'gap0',     [SUBTRACT, ['goal0', 353], ['stock0', 246]],  None,       None,       213,    212,    None],
            [PARAMETER, 'at0',      [5],                                          None,       None,       123,    77,    None],
            # [CONNECTOR, '0',        246,                           'stock0',   'gap0',      0,      0,      None],
            # [CONNECTOR, '1',        353,                           'goal0',    'gap0',      0,      0,      None],
            # [CONNECTOR, '2',        148,                           'gap0',     'flow0',     0,      0,      None],
            # [CONNECTOR, '3',        311,                           'at0',      'flow0',     0,      0,      None]
            ])

    # Set the model to a first order negative feedback loop
    def first_order_positive(self, structure_name='default'):
        # adding a structure that has been pre-defined using multi-dimensional arrays.
        self.add_elements_batch([
            # 0type,    1name/uid,   2value/equation/angle                                   3from,      4to,        5x,     6y,     7pts,
            [STOCK,     'stock0',    [1],                                                    None,       None,       289,    145,    None],
            [FLOW,      'flow0',     [MULTIPLICATION, ['stock0', 100], ['fraction0', 160]],  None,       'stock0',   181,    145,    [(85, 145), (266.5, 145)]],
            [PARAMETER, 'fraction0', [0.1],                                                  None,       None,       163,    251,    None],
        ])

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

    # Add elements on a stock-and-flow level (work with model file handlers)
    def add_stock(self, name, equation, x=0, y=0, structure_name='default'):
        self.structures[structure_name].add_element(name, element_type=STOCK, x=x, y=y, value=equation)
        print('added stock:', name, 'to graph.\n')

    def add_flow(self, name, equation, x=0, y=0, points=None, flow_from=None, flow_to=None, structure_name='default'):
        # Decide if the 'equation' is a function or a constant number
        if type(equation[0]) == int or type(equation[0]) == float:
            # if equation starts with a number
            function = None
            value = equation  # it's a constant
        else:
            function = equation  # it's a function
            value = list()
        self.structures[structure_name].add_element(name, element_type=FLOW, x=x, y=y, function=function, value=value, points=points)

        # If the flow influences a stock, create the causal link
        if flow_to is not None:
            self.structures[structure_name].add_causality(name, flow_to)
        if flow_from is not None:
            self.structures[structure_name].add_causality(name, flow_from)
        # TODO: outflow shoud have a -1 somewhere
        # TODO flow may be used for calculating other variables,
        #  so could have other outgoing causal links
        print('added flow:', name, 'to graph\n')

    def add_aux(self, name, equation, x=0, y=0, structure_name='default'):
        # Decide if this aux is a parameter or variable
        if type(equation[0]) == int or type(equation[0]) == float:
            # if equation starts with a number
            # It's a parameter
            self.structures[structure_name].add_element(name, element_type=PARAMETER, x=x, y=y, function=None, value=equation)
        else:
            # It's a variable, has its own function
            self.structures[structure_name].add_element(name, element_type=VARIABLE, x=x, y=y, function=equation, value=list())
            # Then it is assumed to take information from other variables, therefore causal links should be created.
            # Already implemented in structure's add_element function, not needed here.
            # for info_source_var in equation[1]:
            #     if info_source_var in self.structures[structure_name].sfd.nodes:  # if this info_source is a var
            #         self.structures[structure_name].add_causality(info_source_var, name)
        print('added aux', name, 'to graph.\n')

    def add_connector(self, uid, from_element, to_element, angle=0, structure_name='default'):
        self.structures[structure_name].add_causality(from_element, to_element, uid=uid, angle=angle)

    def add_alias(self, uid, of_element, x=0, y=0, structure_name='default'):
        self.structures[structure_name].add_element(uid, element_type=ALIAS, x=x, y=y, function=of_element)
        print('added alias of', of_element, 'to graph.\n')

    # Clear a run
    def clear_a_run(self, structure_name='default'):
        self.structures[structure_name].clear_value()

    # Reset a structure
    def reset_a_structure(self, structure_name='default'):
        self.structures[structure_name].sfd.clear()

    # Simulate a structure based on a certain set of parameters
    def simulate(self, simulation_time, structure_name='default', dt=0.25):
        print('Simulating...')
        self.simulation_time = simulation_time
        self.dt = dt
        if simulation_time == 0:
            # determine how many steps to run; if not specified, use maximum steps
            total_steps = self.structures[structure_name].maximum_steps
        else:
            total_steps = int(simulation_time/dt)

        # main iteration
        print('\nExecuting Step:', end=' ')
        for i in range(total_steps):
            # stock_behavior.append(structure0.sfd.nodes['stock0']['value'])
            print('%3d' % i, end='  ')
            self.structures[structure_name].step(dt)

    # Draw results
    def draw_results(self, structure_name='default', names=None, rtn=False):
        if names is None:
            names = list(self.structures[structure_name].sfd.nodes)

        self.Figure1 = plt.figure(figsize=(5, 5))

        # plt.subplot(212)  # operate subplot 2
        plt.xlabel('Steps (Time: {} / Dt: {})'.format(self.simulation_time, self.dt))
        plt.ylabel('Behavior')
        y_axis_minimum = 0
        y_axis_maximum = 0
        for name in names:
            print("getting min/max for", name)
            # set the range of axis based on this element's behavior
            # 0 -> end of period (time), 0 -> 100 (y range)

            name_minimum = min(self.structures[structure_name].sfd.nodes[name]['value'])
            name_maximum = max(self.structures[structure_name].sfd.nodes[name]['value'])
            if name_minimum == name_maximum:
                name_minimum *= 2
                name_maximum *= 2
                print('Centered this straight line')

            if name_minimum < y_axis_minimum:
                y_axis_minimum = name_minimum

            if name_maximum > y_axis_maximum:
                y_axis_maximum = name_maximum

            print("Y range: ", y_axis_minimum, '-', y_axis_maximum)
            plt.axis([0, self.simulation_time/self.dt, y_axis_minimum, y_axis_maximum])
            t_series = self.structures[structure_name].sfd.nodes[name]['value']
            print(t_series)
            plt.plot(t_series, label=name)
        plt.legend()
        if rtn:  # if called from external, return the figure without show it.
            return self.Figure1
        else:  # otherwise, show the figure.
            plt.show()

    # Draw graphs
    def draw_graphs(self, structure_name='default', rtn=False):
        self.Figure1 = plt.figure(figsize=(5, 5))
        plt.gca().invert_yaxis()  # invert y-axis to move the origin to upper-left point, matching tkinter's canvas
        pos = nx.get_node_attributes(self.structures[structure_name].sfd, 'pos')
        nx.draw(self.structures[structure_name].sfd, with_labels=True, pos=pos)

        if rtn:  # if called from external, return the figure without show it.
            return self.Figure1
        else:  # otherwise, show the figure.
            plt.show()

    # Draw graphs with curve
    def draw_graphs_with_curve(self, structure_name='default', rtn=False):
        self.Figure1 = plt.figure(figsize=(5, 5))
        ax = plt.gca()
        ax.invert_yaxis()  # invert y-axis to move the origin to upper-left point, matching tkinter's canvas

        # disable all frames/borders
        ax.axes.get_yaxis().set_visible(False)
        ax.axes.get_xaxis().set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)

        pos = nx.get_node_attributes(self.structures[structure_name].sfd, 'pos')
        print(pos)
        self.draw_network(self.structures[structure_name].sfd, pos, ax)
        ax.autoscale()

        if rtn:  # if figure needs to be returned
            print('Engine is returning graph figure.')
            return self.Figure1
        else:
            plt.show()

    # Draw network with FancyArrowPatch
    # Thanks to https://groups.google.com/d/msg/networkx-discuss/FwYk0ixLDuY/dtNnJcOAcugJ
    def draw_network(self, G, pos, ax):
        for n in G:
            print('Engine is drawing network element for', n)
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
    sess0 = Session()
    sess0.first_order_negative()
    sess0.simulate(simulation_time=80)
    # sess0.draw_graphs()
    sess0.draw_graphs_with_curve()
    # after closing the above window ...
    # sess0.draw_results(names=['stock0', 'flow0'])


if __name__ == '__main__':
    main()
