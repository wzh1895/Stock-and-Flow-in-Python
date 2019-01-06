# learned from https://www.cnblogs.com/suwings/p/6358061.html

import networkx as nx
from causalLoopDiagram import CausalLoopDiagram as CLD

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

'''
def _init():
    global _global_model
    _global_model = CLD()

def add_variable():
    pass

def
'''

class Element():
    def __init__(self, name, x, y, eqn="none"):
        self.name = name
        self.eqn = eqn
        self.x = float(x)
        self.y = float(y)
        self.value = None
        self.behavior = []


class Stock(Element):
    def __init__(self, name, x, y, eqn = "none", inflow = "none", outflow = "none"):
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


class Connector():
    def __init__(self, uid, angle, from_var, to_var):
        self.uid = uid
        self.angle = float(angle)
        self.from_var = from_var
        self.to_var = to_var


class Alias():
    def __init__(self, uid, x, y, of):
        self.uid = uid
        self.x = float(x)
        self.y = float(y)
        self.of = of


class Time():
    def __init__(self, end, start=1, dt=0.125):
        self.start = start
        self.end = end
        self.dt = dt
        self.steps = int((self.end-self.start)/self.dt)
        self.current_step = 1
