import xml.dom.minidom
from sdClasses import Stock, Flow, Aux, Connector, Alias

class ModelHandler():
    def __init__(self,filename):
        DOMTree = xml.dom.minidom.parse(filename)
        # self.DOMTree = xml.dom.minidom.parse("./sampleModels/reindeerModel.stmx")
        self.model = DOMTree.documentElement
        self.modelAnalyzer()

    def modelAnalyzer(self):
        '''
        # fetch all variables in the file
        # since there is only one "variables" in the file, the outcome
        # is a list containing only one element of "variables"
        allvariables = model.getElementsByTagName("variables")


        # fetch all stocks/flows/aux/connectors in all variables (the only element in the list)
        stock_defs = allvariables[0].getElementsByTagName("stock")
        flow_defs = allvariables[0].getElementsByTagName("flow")
        aux_defs = allvariables[0].getElementsByTagName("aux")

        '''

        # fetch all views in the file ---> down to the view
        self.allviews = self.model.getElementsByTagName("views")
        self.views = self.allviews[0].getElementsByTagName("view")

        # fetch views for all stocks
        self.stockviews = []
        for stockview in self.views[0].getElementsByTagName("stock"):
            if stockview.hasAttribute("name"):
                self.stockviews.append(stockview)

        # construct stock instances
        self.stocks = []
        for stockview in self.stockviews:
            self.stocks.append(
                Stock(stockview.getAttribute("name"), stockview.getAttribute("x"), stockview.getAttribute("y")))

        # fetch views for all flows
        self.flowviews = []
        for flowview in self.views[0].getElementsByTagName("flow"):
            if flowview.hasAttribute("name"):
                self.flowviews.append(flowview)

        # construct flow instances

        self.flows = []
        for flowview in self.flowviews:
            points = []
            for point in flowview.getElementsByTagName("pt"):
                points.append((point.getAttribute("x"),point.getAttribute("y")))
            self.flows.append(
                Flow(flowview.getAttribute("name"), flowview.getAttribute("x"), flowview.getAttribute("y"),points))

        # fetch views for all auxiliaries
        self.auxviews = []
        for auxview in self.views[0].getElementsByTagName("aux"):
            if auxview.hasAttribute("name"):
                self.auxviews.append(auxview)

        # construct aux instances
        self.auxs = []
        for auxview in self.auxviews:
            self.auxs.append(Aux(auxview.getAttribute("name"), auxview.getAttribute("x"), auxview.getAttribute("y")))
            # print(auxview.getAttribute("name"))

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
