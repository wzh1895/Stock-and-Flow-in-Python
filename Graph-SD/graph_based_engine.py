import networkx as nx
import matplotlib.pyplot as plt


# define functions
def linear(x, a=1, b=0):
    return a * float(x) + b


LINEAR = linear


def subtract(x, y):
    return float(x) - float(y)


SUBTRACT = subtract


def division(x, y):
    return float(x) / float(y)


DIVISION = division


# define constants
STOCK = 'stock'
FLOW = 'flow'
VARIABLE = 'variable'
PARAMETER = 'parameter'
CONNECTOR = 'connector'


class Structure(object):
    def __init__(self):
        self.sfd = nx.MultiDiGraph()

    def add_element(self, element_name, element_type, function=None, value=None):
        # this 'function' is a list, containing the function it self and its parameters
        # this 'value' is also a list, containing historical value throughout this simulation
        self.sfd.add_node(element_name, element_type=element_type, function=function, value=value)

    def add_causality(self, from_element, to_element):
        self.sfd.add_edge(from_element, to_element)

    def display_elements(self):
        print('All elements in this SFD:')
        print(self.sfd.nodes.data())

    def display_element(self, name):
        print('Attributes of element {}:'.format(name))
        print(self.sfd.nodes[name])

    def display_causalities(self):
        print('All causalities in this SFD:')
        print(self.sfd.edges)

    def display_causality(self, from_element, to_element):
        print('Causality from {} to {}:'.format(from_element, to_element))
        print(self.sfd[from_element][to_element])

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
            params = self.sfd.nodes[name]['function'][1:]  # extract all parameters needed by this function
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
        print('All flows dt:', flows_dt)

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

        # updating stocks values
        for stock in affected_stocks.keys():
            # calculate the new value for this stock and add it to the end of its value list
            self.sfd.nodes[stock]['value'].append(self.sfd.nodes[stock]['value'][-1] + affected_stocks[stock])


class Session(object):
    def __init__(self):
        self.simulation_time = 13
        self.dt = 0.25
        self.structures = dict()
        self.add_structure()

    def add_structure(self, structure_name='default'):
        self.structures[structure_name] = Structure()

    # Set the model to a first order negative feedback loop
    def first_order_negative(self, structure_name='default'):
        # adding a structure that has been pre-defined using multi-dimensional arrays.
        self.add_elements_batch([
            # type,     name,       value/equation/angle            from,       to,         x,      y,      pts,
            [STOCK,     'stock0',   [100],                          None,       None,       489,    245,    None],
            [FLOW,      'flow0',    [DIVISION, 'gap0', 'at0'],      None,       'stock0',   381,    245,    None],
            [PARAMETER, 'goal0',    [20],                           None,       None,       363,    351,    None],
            [VARIABLE,  'gap0',     [SUBTRACT, 'goal0', 'stock0'],  None,       None,       413,    312,    None],
            [PARAMETER, 'at0',      [5],                            None,       None,       323,    177,    None],
            [CONNECTOR, '0',        246,                           'stock0',   'gap0',      0,      0,      None],
            [CONNECTOR, '1',        353,                           'goal0',    'gap0',      0,      0,      None],
            [CONNECTOR, '2',        148,                           'gap0',     'flow0',     0,      0,      None],
            [CONNECTOR, '3',        311,                           'at0',      'flow0',     0,      0,      None]
            ])

    # Add elements to a structure in a batch (something like a script)
    # Enable using of multi-dimensional arrays.
    def add_elements_batch(self, elements):
        for element in elements:
            if element[0] == STOCK:
                self.add_stock(name=element[1],
                               equation=element[2])
            elif element[0] == FLOW:
                self.add_flow(name=element[1],
                              equation=element[2],
                              flow_from=element[3],
                              flow_to=element[4])
            elif element[0] == PARAMETER or element[0] == VARIABLE:
                self.add_aux(element[1], element[2])
            elif element[0] == CONNECTOR:
                self.add_connector(element[1], element[3], element[4], angle=element[2])

    # Add elements on a stock-and-flow level (work with model file handlers)
    def add_stock(self, name, equation, x=0, y=0, structure_name='default'):
        self.structures[structure_name].add_element(name,
                                                    STOCK,
                                                    value=equation)

    def add_flow(self, name, equation, x=0, y=0, points=None, flow_from=None, flow_to=None, structure_name='default'):
        # Decide if the 'equation' is a function or a constant number
        if type(equation[0]) == int or type(equation[0]) == float:
            # if equation starts with a number
            function = None
            value = equation
        else:
            function = equation
            value = list()
        self.structures[structure_name].add_element(name, FLOW, function=function, value=value)

        # If the flow influences a stock, create the causal link
        if flow_to is not None:
            self.structures[structure_name].add_causality(name, flow_to)
        if flow_from is not None:
            self.structures[structure_name].add_causality(name, flow_from)
            # TODO: outflow shoud have a -1 somewhere
        # TODO flow may be used for calculating other variables,
        #  so could have other outgoing causal links

    def add_aux(self, name, equation, x=0, y=0, structure_name='default'):
        # Decide if this aux is a parameter or variable
        if type(equation[0]) == int or type(equation[0]) == float:
            # if equation starts with a number
            # It's a parameter
            self.structures[structure_name].add_element(name,
                                                        PARAMETER,
                                                        function=None,
                                                        value=equation)
        else:
            # It's a variable
            self.structures[structure_name].add_element(name,
                                                        VARIABLE,
                                                        function=equation,
                                                        value=list())

    def add_connector(self, uid, from_element, to_element, angle=0, structure_name='default'):
        self.structures[structure_name].add_causality(from_element, to_element)

    def add_alias(self, uid, of_element, x=0, y=0, structure_name='default'):
        pass

    # Simulate a structure based on a certain set of parameters
    def simulate(self,
                 structure_name='default',
                 simulation_time=13,
                 dt=0.25):
        self.simulation_time = simulation_time
        self.dt = dt
        if simulation_time == 0:
            # determine how many steps to run; if not specified, use maximum steps
            total_steps = self.structures[structure_name].maximum_steps
        else:
            total_steps = int(simulation_time/dt)

        # main iteration
        for i in range(total_steps):
            # stock_behavior.append(structure0.sfd.nodes['stock0']['value'])
            print('\nExecuting Step {} :\n'.format(i))
            self.structures[structure_name].step(dt)

    # Draw graphs
    def draw_graphs(self, structure_name='default', names=None):
        if names is None:
            names = list(self.structures[structure_name].sfd.nodes)

        plt.figure(figsize=(10, 5))
        plt.subplot(121)
        plt.xlabel('Time')
        plt.ylabel('Behavior')
        y_axis_minimum = 0
        y_axis_maximum = 0
        for name in names:
            # set the range of axis based on this element's behavior
            # 0 -> end of period (time), 0 -> 100 (y range)
            try:
                name_minimum = min(self.structures[structure_name].sfd.nodes[name]['value'])
            except:  # if this element is a constant, there's no min
                name_minimum = self.structures[structure_name].sfd.nodes[name]['value'][-1]
            if name_minimum < y_axis_minimum:
                y_axis_minimum = name_minimum

            try:
                name_maximum = max(self.structures[structure_name].sfd.nodes[name]['value'])
            except:  # if this element is a constant, there's no max
                name_maximum = self.structures[structure_name].sfd.nodes[name]['value'][-1]
            if name_maximum > y_axis_maximum:
                y_axis_maximum = name_maximum

            plt.axis([0, self.simulation_time, y_axis_minimum, y_axis_maximum])
            plt.plot(self.structures[structure_name].sfd.nodes[name]['value'], label=name)
        plt.legend()

        plt.subplot(122)
        # labels = nx.get_node_attributes(structure0.sfd, 'value')
        # nx.draw(structure0.sfd, labels=labels)
        nx.draw(self.structures[structure_name].sfd, with_labels=True)
        plt.show()


def main():
    sess0 = Session()
    sess0.first_order_negative()
    sess0.simulate(simulation_time=80)
    sess0.draw_graphs(names=['stock0', 'flow0'])


if __name__ == '__main__':
    main()
