import math
import xml.dom.minidom
from tkinter import *
from tkinter import filedialog
from tkinter import ttk

import matplotlib
matplotlib.use('TkAgg')

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import os, shutil

from sdClasses import Stock, Flow, Aux, Connector, Alias

class SFDCanvas(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.xmost = 300
        self.ymost = 300

        self.canvas = Canvas(self)

        self.hbar = Scrollbar(self,orient = HORIZONTAL)
        self.hbar.pack(side = BOTTOM, fill = X)
        self.hbar.config(command = self.canvas.xview)

        self.vbar = Scrollbar(self,orient = VERTICAL)
        self.vbar.pack(side = RIGHT, fill = Y)
        self.vbar.config(command = self.canvas.yview)

        self.createWidgets()

        self.pack(fill=BOTH, expand=1)
        self.filename = ''

    def create_stock(self, x, y, w, h, label):
        '''
        Center x, Center y, width, height, label
        '''
        self.canvas.create_rectangle(x - w * 0.5, y - h * 0.5, x + w * 0.5, y + h * 0.5, fill="#fff")
        self.canvas.create_text(x, y + 30, anchor=CENTER, font=("Arial", 13), text=label)

    def create_flow(self, x, y, xA, yA, xB, yB, l, r, label):
        '''
        Starting point x, y, ending point x, y, length, circle radius, label
        '''
        self.canvas.create_line(xA, yA, xB, yB, arrow=LAST)
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="#fff")
        self.canvas.create_text(x, y + r + 10, anchor=CENTER, font=("Arial", 13), text=label)

    def create_aux(self, x, y, r, label):
        '''
        Central point x, y, radius, label
        '''
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="#fff")
        self.canvas.create_text(x, y + r + 10, anchor=CENTER, font=("Arial", 13), text=label)

    def create_alias(self, x, y, r, label):
        '''
        Central point x, y, radius, label
        '''
        self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="gray70")
        self.canvas.create_text(x, y, anchor=CENTER, font=("Arial", 10), text="G")
        self.canvas.create_text(x, y + r + 10, anchor=CENTER, font=("Arial", 13, "italic"), text=label)

    def create_connector(self, xA, yA, xB, yB, angle, color='black'):
        # self.create_dot(xA,yA,3,'black')
        # self.create_dot(xB,yB,3,'black')
        alpha = math.radians(angle)
        if math.pi < alpha < math.pi * 2:
            alpha -= math.pi * 2
        beta = math.atan2((yA - yB), (xB - xA))  # angle between A->B and x-positive
        print('alpha in degrees, ', math.degrees(alpha), 'beta in degrees, ', math.degrees(beta))

        # calculate the center of circle

        rad_radiusA = alpha - math.pi * 0.5  # radiant of radius of the circle going out from A
        print('rad_radiusA (degrees), ', math.degrees(rad_radiusA), 'radians, ', rad_radiusA)
        gA = math.tan(rad_radiusA)
        print('gradiantA, ', gA)
        if xB != xA:
            gAB = (yA - yB) / (xB - xA)  # y axis inversed, could be 'zero division'
        else:
            gAB = 99.99
        print('gradiantAB, ', gAB)

        gM = (-1) / gAB
        print('gradiantM, ', gM)
        xM = (xA + xB) / 2
        yM = (yA + yB) / 2
        print("M's coordinate", xM, yM)

        xC = (yA + gA * xA - gM * xM - yM) / (gA - gM)
        yC = yA - gA * (xC - xA)
        print("A's coordinate: ", xA, yA)
        print("C's coordinate: ", xC, yC)

        #self.create_dot(xC, yC, 2, color, str(angle))  # draw center of the circle
        # TODO: when C and A are calculated to be the same point (and in fact not)
        rad_CA = math.atan2((yC - yA), (xA - xC))
        rad_CB = math.atan2((yC - yB), (xB - xC))

        print('rad_CA, ', rad_CA, 'rad_CB, ', rad_CB)


        # calculate radius

        radius = (pow((xB - xC), 2) + pow((yC - yB), 2)) ** 0.5
        baseArc = math.atan2(yC - yA, xA - xC)


        print('baseArc in degrees, ', math.degrees(baseArc))

        print("checking youhu or liehu")
        # vectors, this part seems to be correct

        vecStarting = [math.cos(alpha), math.sin(alpha)]
        vecAtoB = [xB - xA, yA - yB]
        print('vecStarting, ', vecStarting, 'vecAtoB, ', vecAtoB)
        angleCos = self.cosFormula(vecStarting, vecAtoB)
        print('Cosine of the angle in Between, ', angleCos)

        # checking youhu or liehu the direction

        inverse = 1

        if angleCos < 0:  # you hu
            print('deg_CA, ', math.degrees(rad_CA),'deg_CB',math.degrees(rad_CB))
            diff = rad_CB-rad_CA
            print('youhu')
        else: # lie hu
            if rad_CA*rad_CB<0 and rad_CA <= rad_CB: # yi hao
                diff = rad_CB-rad_CA
                if diff > math.pi:
                    diff = abs(diff) - math.pi*2
            elif rad_CA*rad_CB<0 and rad_CA > rad_CB:
                diff = math.pi*2-rad_CA+rad_CB
                if diff > math.pi:
                    diff = diff - math.pi*2
            elif rad_CA*rad_CB>0 and rad_CA > rad_CB:
                diff = rad_CB-rad_CA
                if diff > math.pi:
                    diff = math.pi*2 - diff
            elif rad_CA*rad_CB>0 and rad_CA < rad_CB:
                diff = rad_CB-rad_CA
                if diff > math.pi:
                    diff = math.pi*2 - diff
            else:
                diff = rad_CB-rad_CA
            print('liehu')
        print('final diff in degrees, ', math.degrees(diff))
        # generate new points

        x = [xA]
        y = [yA]
        n = 7

        for i in range(n):
            baseArc = baseArc + diff / (n + 1) * inverse
            x1 = xC + radius * math.cos(baseArc)
            x.append(x1)
            y1 = yC - radius * math.sin(baseArc)
            y.append(y1)
            # Draw dots of the connectors, if you would like
            #self.create_dot(x1,y1,2,'gray',str(i))

        x.append(xB)
        y.append(yB)

        self.canvas.create_line(x[0], y[0], x[1], y[1], x[2], y[2], x[3], y[3], x[4], y[4], x[5], y[5], x[6], y[6],
                                x[7], y[7], x[8], y[8], smooth=True, fill='maroon2', arrow=LAST)

        print('\n')

    def create_dot(self, x, y, r, color, label=''):
        self.canvas.create_oval(x - r, y - r, x + r, y + r, outline=color, fill=color)
        self.canvas.create_text(x, y - 10, text=label)

    def cosFormula(self, a, b):
        '''
        calculate the cosine value of a angle between 2 vectors.
        :param a:
        :param b:
        :return:
        '''
        l = 0
        m = 0
        n = 0
        for i in range(2):
            l += a[i] * b[i]
            m += a[i] ** 2
            n += b[i] ** 2
        return l / ((m * n) ** 0.5)

    def locateVar(self, name):
        name = name.replace("_", " ")
        # print(name)
        for s in self.stocks:
            nameWithoutN = s.name.replace("\\n", " ")
            if nameWithoutN == name:
                return [s.x, s.y]
        for f in self.flows:
            nameWithoutN = f.name.replace("\\n", " ")
            if nameWithoutN == name:
                return [f.x, f.y]
        for a in self.auxs:
            nameWithoutN = a.name.replace("\\n", " ")
            # print(nameWithoutN)
            if nameWithoutN == name:
                return [a.x, a.y]

    def locateAlias(self, uid):
        # print("locateAlias is called")
        for al in self.aliases:
            if al.uid == uid:
                return [al.x, al.y]

    # Here starts Widgets and Commands

    def createWidgets(self):
        fm_1 = Frame(self.master)
        self.lb = Label(fm_1,text='Load and display a Stella SD Model')
        self.lb.pack()
        fm_1.pack(side = TOP)

        fm_2 = Frame(fm_1)
        self.btn1 = Button(fm_2, text="Select model", command = self.fileLoad)
        self.btn1.pack(side = LEFT)
        self.btn2 = Button(fm_2, text="Run", command = self.simulationHandler)
        self.btn2.pack(side = LEFT)
        self.comboxlist = ttk.Combobox(fm_2)
        self.variablesInModel = ["Variable"]
        self.comboxlist["values"] = self.variablesInModel
        self.comboxlist.current(0)
        self.comboxlist.bind("<<ComboboxSelected>>",self.selectVariable)
        self.comboxlist.pack(side = LEFT)
        self.btn3 = Button(fm_2, text="Show Figure", command = self.showFigure)
        self.btn3.pack(side = LEFT)
        self.btn4 = Button(fm_2, text="Reset canvas", command = self.resetCanvas)
        self.btn4.pack(side = LEFT)
        fm_2.pack(side = TOP)

    def fileLoad(self):
        self.filename = filedialog.askopenfilename()

        if self.filename != '':
            self.lb.config(text = "File selected: " + self.filename)
            self.fileHandler(self.filename)
            self.modelAnalyzer()
            self.modelDrawer()

        else:
            self.lb.config(text = "No file is selected.")

    def resetCanvas(self):
        self.canvas.delete('all')
        self.lb.config(text = 'Load and display a Stella SD Model')
        self.variablesInModel = ["Variable"]
        self.comboxlist["values"] = self.variablesInModel
        self.comboxlist.current(0)
        self.xmost = 300
        self.ymost = 300
        self.canvas.config(width = self.xmost, height = self.ymost, scrollregion = (0,0,self.xmost,self.ymost))

    def fileHandler(self, filename):
        DOMTree = xml.dom.minidom.parse(filename)
        #self.DOMTree = xml.dom.minidom.parse("./sampleModels/reindeerModel.stmx")
        self.model = DOMTree.documentElement

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
            self.flows.append(
                Flow(flowview.getAttribute("name"), flowview.getAttribute("x"), flowview.getAttribute("y"),
                     flowview.getElementsByTagName("pt")[0].getAttribute("x"),
                     flowview.getElementsByTagName("pt")[0].getAttribute("y"),
                     flowview.getElementsByTagName("pt")[1].getAttribute("x"),
                     flowview.getElementsByTagName("pt")[1].getAttribute("y")))

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

    def modelDrawer(self):
        # now starts the 'drawing' part
        self.canvas.config(width = self.xmost, height = self.ymost, scrollregion = (0,0,self.xmost,self.ymost))

        #self.canvas.config(width = wid, height = hei)
        self.canvas.config(xscrollcommand = self.hbar.set, yscrollcommand = self.vbar.set)


        # set common parameters
        width1 = 46
        height1 = 35
        length1 = 115
        radius1 = 5

        # draw connectors
        for c in self.connectors:
            print("\n")
            print(c.uid)
            # from
            print("c.from_var:", c.from_var, "childNodes:", c.from_var.childNodes)

            if len(c.from_var.childNodes) > 1:  # if this end is on an alias
                print("it has more than 1 childNodes, so alias")
                from_cord = self.locateAlias(c.from_var.childNodes[1].getAttribute("uid"))
            else:
                print("it has childNodes, so normal variable")
                print("c.from_var.childNodes[0].data: ", c.from_var.childNodes[0].data)
                from_cord = self.locateVar(c.from_var.childNodes[0].data)

            print("from_cord: ", from_cord)
            # to
            print("c.to_var", c.to_var, "childNodes:", c.to_var.childNodes)
            if len(c.to_var.childNodes) > 1:  # if this end is no an alias
                print("it has more than 1 childNodes, so alias")
                to_cord = self.locateAlias(c.to_var.childNodes[1].getAttribute("uid"))
            else:
                print("it has childNodes, so normal variable")
                print("c.to_var.childNodes[0].data: ", c.to_var.childNodes[0].data)
                to_cord = self.locateVar(c.to_var.childNodes[0].data)

            print("to_cord: ", to_cord)
            from_to_cord = from_cord + to_cord
            self.create_connector(from_to_cord[0], from_to_cord[1], from_to_cord[2], from_to_cord[3] - 8,
                                  c.angle)  # minus 8: the arrow it self not consumed

        # draw stocks
        for s in self.stocks:
            self.create_stock(s.x, s.y, width1, height1, s.name)
            if s.x> self.xmost:
                self.xmost = s.x
            if s.y> self.ymost:
                self.ymost = s.y

        # draw flows
        for f in self.flows:
            self.create_flow(f.x, f.y, f.xA, f.yA, f.xB, f.yB, (pow((f.xB - f.xA), 2) + pow((f.yB - f.yA), 2)) ** 0.5,
                             radius1, f.name)
            if f.x > self.xmost:
                self.xmost = f.x
            if f.y > self.ymost:
                self.ymost = f.y

        # draw auxs
        for a in self.auxs:
            self.create_aux(a.x, a.y, radius1, a.name)
            if a.x > self.xmost:
                self.xmost = a.x
            if a.y > self.ymost:
                self.ymost = a.y

        # draw aliases
        for al in self.aliases:
            self.create_alias(al.x, al.y, radius1, al.of.replace('_', ' '))
            if al.x > self.xmost:
                self.xmost = al.x
            if al.y > self.ymost:
                self.ymost = al.y

        self.xmost += 150
        self.ymost += 100
        print('Xmost,',self.xmost,'Ymost,',self.ymost)
        self.canvas.config(width = self.xmost, height = self.ymost, scrollregion = (0,0,self.xmost,self.ymost))
        self.canvas.pack(side = LEFT, expand=1, fill=BOTH)

    # Here starts the simulation part

    def simulationHandler(self):

        import pysd

        if self.filename != '':
            new_name = self.filename[:-5]+".xmile"
            shutil.copy(self.filename,new_name)
            self.model_run = pysd.read_xmile(new_name)
            os.remove(new_name)
            os.remove(new_name[:-6]+".py")
            self.results = self.model_run.run()
            self.variablesInModel = self.results.columns.values.tolist()
            self.variablesInModel.remove("TIME")
            self.comboxlist["values"] = self.variablesInModel

    def selectVariable(self,*args):
        self.selectedVariable = self.comboxlist.get()

    def showFigure(self):
        f = Figure(figsize=(5, 4), dpi=100)
        a = f.add_subplot(111)
        x = self.results['TIME'].tolist()
        y = self.results[self.selectedVariable].tolist()
        a.plot(x,y)
        a.set_title(self.selectedVariable)
        a.set_xlabel('Time')
        a.set_ylabel(self.selectedVariable)

        figure1 = GraphWindow(self.selectedVariable, f)


class GraphWindow():
    def __init__(self,title,figure):
        top = Toplevel()
        top.title = title
        graph = FigureCanvasTkAgg(figure, master = top)
        graph.draw()
        graph._tkcanvas.pack()

def main():
    root = Tk()
    wid = 800
    hei = 600
    Frame1 = SFDCanvas(root)
    root.wm_title("Stock and Flow Canvas")
    root.geometry(str(wid)+"x"+str(hei)+"+100+100")
    #app = SFDCanvas(master = root)
    root.mainloop()

if __name__ == '__main__':
    main()
