# learned from https://www.cnblogs.com/suwings/p/6358061.html

import networkx as nx
from causalLoopDiagram import CausalLoopDiagram as CLD

"""

Make model elements available in a global way to all modules.

"""


def _init():
    global _global_dict
    _global_dict = {}


def set_value(key, value):
    """ define a global variable """
    _global_dict[key] = value


def get_value(key, def_value=None):
    """ get a global variable, return default if not existing """
    try:
        return _global_dict[key]
    except KeyError:
        return def_value


def get_keys():
    return _global_dict.keys()


# TODO Wrap instances in a Class of Model

'''
def _init():
    global _global_model
    _global_model = CLD()

def add_variable():
    pass

def
'''
