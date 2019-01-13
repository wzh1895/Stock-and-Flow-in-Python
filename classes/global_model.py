# A way to globalize, learned from https://www.cnblogs.com/suwings/p/6358061.html

import networkx as nx
import matplotlib.pyplot as plt

"""

Make model elements available in a global way to all modules.

"""


def _init():
    global _global_dict
    _global_dict = {}
    global _global_stocks
    _global_stocks = {}
    global _global_flows
    _global_flows = {}
    global _global_auxs
    _global_auxs = {}
    global _global_connectors
    _global_connectors = {}


def set_value(key, value):
    """ define a global variable """
    _global_dict[key] = value

    if type(value) == Stock:
        _global_stocks[key] = value
    if type(value) == Flow:
        _global_flows[key] = value
    if type(value) == Aux:
        _global_auxs[key] = value
    if type(value) == Connector:
        _global_connectors[key] = value


def get_value(key, def_value=None):
    """ get a global variable, return default if not existing """
    try:
        return _global_dict[key]
    except KeyError:
        return def_value


def get_keys():
    return _global_dict.keys()


def get_stocks_keys():
    return _global_stocks.keys()


def get_stocks():
    return _global_stocks.values()


def get_flows_keys():
    return _global_flows.keys()


def get_flows():
    return  _global_flows.values()


def get_auxs_keys():
    return _global_auxs.keys()


def get_auxs():
    return _global_auxs.values()


def get_connectors_keys():
    return _global_connectors.keys()


def get_connectors():
    return _global_connectors.values()


# TODO Wrap instances in a Class of Model


class Model(object):
    """
    The class for System Dynamics Models, Including SFD and CLD.
    """
    def __init__(self, name='default'):
        self.__structure = nx.MultiDiGraph()
        self.name = name
        self.uid = 1

        self.stocks = []
        self.flows = {}
        self.auxs = []
        self.connectors = []

        #self.timers = {}
        self.timer = Time()

    def add_stock(self, name, x, y, eqn, inflow='none', outflow='none'):
        self.__structure.add_node(name, uid=self.uid, type='stock',
                                var=Stock(name=name, x=x, y=y, eqn=eqn,inflow=inflow, outflow=outflow)
                                )
        print('Stock added\tname:', name, '\tuid:', self.uid)
        self.stocks.append(name)
        self.uid += 1

    def add_flow(self, name, x, y, pts, eqn):
        self.__structure.add_node(name, uid=self.uid, type='flow',
                                  var=Flow(name=name, x=x, y=y, pts=pts, eqn=eqn)
                                )
        print('Flow added\tname:', name, '\tuid:', self.uid)
        self.flows[name] = 0
        self.uid += 1

    def add_aux(self, name, x, y, eqn):
        self.__structure.add_node(name, uid=self.uid, type='aux',
                                var=Aux(name=name, x=x, y=y, eqn=eqn)
                                )
        print('Aux added\tname:', name, '\tuid:', self.uid)
        self.auxs.append(name)
        self.uid += 1

    def add_connector(self, angle, from_var, to_var):
        #self.structure.add_edge(u_of_edge=from_var, v_of_edge=to_var, angle=float(angle))
        self.__structure.add_edge(u_for_edge=from_var, v_for_edge=to_var, angle=float(angle))
        print('Connector added\tfrom', from_var, '\tto', to_var)

    def set_timer(self, start, end, dt, name='time1'):
        # self.timers[name] = Time(start=start, end=end, dt=dt)
        self.timer = Time(start=start, end=end, dt=dt)
        print('Time set\tstart:', start, '\tend:', end, '\tdt:', dt)

    def print_all_variables(self):
        print(self.__structure.nodes(data=True))

    def print_all_connectors(self):
        print(self.__structure.edges)

    def get_var_by_name(self, name):
        return self.__structure.nodes[name]

    def get_value_by_name(self, name):
        return self.__structure.nodes[name]['eqn']

    def set_value_by_name(self, name, value):
        self.__structure.nodes[name]['value'] = value

    def draw_cld(self):
        nx.draw_circular(self.__structure, with_labels=True)
        plt.show()
'''
    def run(self):
        for flow in self.flows:
            #self.flows[flow] = self.__structure.nodes[flow]['var']()
            try:
                self.set_value_by_name(flow, float(self.get_value_by_name(flow)))
            except ValueError:
                self.set_value_by_name(flow, exec("(self.get_value_by_name('goal1')-self.get_value_by_name('stock1'))/self.get_value_by_name('at1')"))

        for stock in self.stocks:
            try:
                self.__structure.nodes[stock]['var'].change_in_stock(self.flows[self.__structure.nodes[stock]['var'].inflow]*self.timer.dt)
            except:
                pass
            try:
                self.__structure.nodes[stock]['var'].change_in_stock(self.flows[self.__structure.nodes[stock]['var'].outflow]*self.timer.dt)
            except:
                pass

        self.timer.current_step += 1
'''

# TODO Wrap instances in a Class of Model -- The end

class Element(object):
    def __init__(self, name, x, y, eqn="none"):
        self.name = name
        self.eqn = eqn
        self.x = float(x)
        self.y = float(y)
        self.value = None
        self.behavior = []


class Stock(Element):
    def __init__(self, name, x, y, eqn="none", inflow="none", outflow="none"):
        super(Stock, self).__init__(name, x, y, eqn)
        self.inflow = inflow
        self.outflow = outflow
        try:
            self.value = float(self.eqn)
        except ValueError:
            exec('self.value='+self.eqn)
        self.behavior.append(self.value)

    def __call__(self):
        return self.value

    def change_in_stock(self, amount):
        self.value += amount
        self.behavior.append(self.value)


class Flow(Element):
    def __init__(self, name, x, y, pts, eqn="none"):
        super(Flow, self).__init__(name, x, y, eqn)
        self.pts = pts

    def __call__(self):
        try:
            self.value = float(self.eqn)
            return self.value
        except ValueError:
            exec('self.value='+self.eqn)
            return self.value


class Aux(Element):
    def __init__(self, name, x, y, eqn="none"):
        super(Aux, self).__init__(name, x, y, eqn)

    def __call__(self):
        try:
            self.value = float(self.eqn)
            return self.value
        except ValueError:
            exec('self.value='+self.eqn)
            return self.value


class Connector(object):
    def __init__(self, uid, angle, from_var, to_var):
        self.uid = uid
        self.angle = float(angle)
        self.from_var = from_var
        self.to_var = to_var


class Alias(object):
    def __init__(self, uid, x, y, of):
        self.uid = uid
        self.x = float(x)
        self.y = float(y)
        self.of = of


class Time(object):
    def __init__(self, end=25, start=1, dt=0.125):
        self.start = start
        self.end = end
        self.dt = dt
        self.steps = int((self.end-self.start)/self.dt)
        self.current_step = 1
