import xml.dom.minidom
from StockAndFlowInPython.depreciated.classes import Stock, Flow, Aux, Connector, Alias


class ModelHandler(object):
    def __init__(self, filename):
        DOMTree = xml.dom.minidom.parse(filename)
        self.model = DOMTree.documentElement
        self.modelAnalyzer()

    def modelAnalyzer(self):

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

        # fetch views for all stocks
        self.stockviews = []
        for stockview in self.views[0].getElementsByTagName("stock"):
            if stockview.hasAttribute("name"):
                self.stockviews.append(stockview)

        # construct stock instances
        self.stocks = []
        for stockview in self.stockviews:
            name = stockview.getAttribute("name")
            x = stockview.getAttribute("x")
            y = stockview.getAttribute("y")
            for stock_definition in self.stock_definitions:
                if stock_definition.getAttribute("name") == name:
                    eqn = stock_definition.getElementsByTagName("eqn")[0].firstChild.data
                    break

            self.stocks.append(Stock(name=name, x=x, y=y, eqn=eqn))

        # fetch views for all flows
        self.flowviews = []
        for flowview in self.views[0].getElementsByTagName("flow"):
            if flowview.hasAttribute("name"):
                self.flowviews.append(flowview)

        # construct flow instances

        self.flows = []
        for flowview in self.flowviews:
            name = flowview.getAttribute("name")
            x = flowview.getAttribute("x")
            y = flowview.getAttribute("y")
            for flow_definition in self.flow_definitions:
                if flow_definition.getAttribute("name") == name:
                    eqn = flow_definition.getElementsByTagName("eqn")[0].firstChild.data
                    break
            points = []
            for point in flowview.getElementsByTagName("pt"):
                points.append((point.getAttribute("x"), point.getAttribute("y")))
            self.flows.append(Flow(name=name, x=x, y=y, pts=points, eqn= eqn))

        # fetch views for all auxiliaries
        self.auxviews = []
        for auxview in self.views[0].getElementsByTagName("aux"):
            if auxview.hasAttribute("name"):
                self.auxviews.append(auxview)

        # construct aux instances
        self.auxs = []
        for auxview in self.auxviews:
            name = auxview.getAttribute("name")
            x = auxview.getAttribute("x")
            y = auxview.getAttribute("y")
            for aux_definition in self.aux_definitions:
                if aux_definition.getElementsByTagName("name") == name:
                    eqn = aux_definition.getElementsByTagName("eqn")[0].firstChild.data
                    break
            self.auxs.append(Aux(name=name, x=x, y=y, eqn=eqn))

        # fetch views for all connectors
        self.connectorviews = []
        for connectorview in self.views[0].getElementsByTagName("connector"):
            if connectorview.hasAttribute("uid"):
                self.connectorviews.append(connectorview)

        # construct connector instances
        self.connectors = []
        for connectorview in self.connectorviews:
            # don't use ".data" for from or to tags, since they may be alias
            self.connectors.append(Connector(connectorview.getAttribute("uid"), connectorview.getAttribute("angle"),
                                             connectorview.getElementsByTagName("from")[0],
                                             connectorview.getElementsByTagName("to")[0]))

        # fetch views for all aliases
        self.aliasviews = []
        for aliasview in self.views[0].getElementsByTagName("alias"):
            # distinguish definition of alias from refering to it
            if aliasview.hasAttribute("color"):
                self.aliasviews.append(aliasview)
        print(self.aliasviews)

        # construct alias instances
        self.aliases = []
        for aliasview in self.aliasviews:
            # print("Constrcting Alias: ", aliasview.getElementsByTagName("of"), "of ", aliasview.getElementsByTagName("of")[0].childNodes[0].data)
            self.aliases.append(
                Alias(aliasview.getAttribute("uid"), aliasview.getAttribute("x"), aliasview.getAttribute("y"),
                      aliasview.getElementsByTagName("of")[0].childNodes[0].data))

        # print("toal alias", len(self.aliases))
