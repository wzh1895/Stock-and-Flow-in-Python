import networkx as nx


class Var(object):
    def __init__(self):
        pass


class Model(object):
    def __init__(self):

        self.md = nx.MultiDiGraph()
        self.namespace = {}

        self.md.add_node('a', eqn='2')
        self.namespace['a'] = self.md.nodes['a']['eqn']

        self.md.add_node('b', eqn='3')
        self.namespace['b'] = self.md.nodes['b']['eqn']

        self.md.add_node('c', eqn='a+b')
        self.namespace['c'] = self.md.nodes['c']['eqn']
        # self.md.add_edge(u_for_edge='a', v_for_edge='c')
        # self.md.add_edge(u_for_edge='a', v_for_edge='c')

        self.md.add_node('d', eqn='a+c')
        self.namespace['d'] = self.md.nodes['d']['eqn']
        # self.md.add_edge(u_for_edge='a', v_for_edge='d')

        print('a:', self.get('a'))
        print('b:', self.get('b'))
        print('c:', self.get('c'))
        print('d:', self.get('d'))

    def get(self, variable):
        try:
            temp0 = float(self.md.nodes[variable]['eqn'])
            print('try OK', temp0)
            return temp0
        except ValueError:
            print('try not OK 1', self.md.nodes[variable]['eqn'])
            temp1 = eval(self.md.nodes[variable]['eqn'], self.namespace)
            print('try not OK 2', temp1)
            return float(temp1)
            # TODO Parsing!!


model1 = Model()
