import networkx as nx


class CausalLoopDiagram(nx.DiGraph):
    def __init__(self):
        super(CausalLoopDiagram, self).__init__()
