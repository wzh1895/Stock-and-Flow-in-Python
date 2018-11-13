import tkinter as tk
import sys
import math
import xml.dom.minidom

from sdClasses import Stock, Flow, Aux, Connector, Alias

class SFDCanvas(tk.Frame):
    def __init__(self):
        tk.Frame.__init__(self)
        self.initUI()

    def initUI(self):
        self.master.title("Stock and Flow Canvas")
        self.pack(fill=tk.BOTH, expand=1)

        self.canvas = tk.Canvas(self)
        
        # first read in xml, make lists for stocks, flow, connectors, auxs; then draw them.
        # now starts the 'reading' part
        # open XML file with minidom
        filename = sys.argv[1]
        DOMTree = xml.dom.minidom.parse(filename)
        model = DOMTree.documentElement
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
        self.allviews = model.getElementsByTagName("views")
        self.views = self.allviews[0].getElementsByTagName("view")

        # fetch views for all stocks
        self.stockviews = []
        for stockview in self.views[0].getElementsByTagName("stock"):
            if stockview.hasAttribute("name"):
                self.stockviews.append(stockview)

        # construct stock instances
        self.stocks = []
        for stockview in self.stockviews:
            self.stocks.append(Stock(stockview.getAttribute("name"),stockview.getAttribute("x"),stockview.getAttribute("y")))

        # fetch views for all flows
        self.flowviews = []
        for flowview in self.views[0].getElementsByTagName("flow"):
            if flowview.hasAttribute("name"):
                self.flowviews.append(flowview)

        # construct flow instances

        self.flows = []
        for flowview in self.flowviews:
            self.flows.append(Flow(flowview.getAttribute("name"),flowview.getAttribute("x"),flowview.getAttribute("y"),flowview.getElementsByTagName("pt")[0].getAttribute("x"),flowview.getElementsByTagName("pt")[0].getAttribute("y"),flowview.getElementsByTagName("pt")[1].getAttribute("x"),flowview.getElementsByTagName("pt")[1].getAttribute("y")))

        # fetch views for all auxiliaries
        self.auxviews = []
        for auxview in self.views[0].getElementsByTagName("aux"):
            if auxview.hasAttribute("name"):
                self.auxviews.append(auxview)

        # construct aux instances
        self.auxs = []
        for auxview in self.auxviews:
            self.auxs.append(Aux(auxview.getAttribute("name"),auxview.getAttribute("x"),auxview.getAttribute("y")))
            #print(auxview.getAttribute("name"))

        # fetch views for all connectors
        self.connectorviews = []
        for connectorview in self.views[0].getElementsByTagName("connector"):
            if connectorview.hasAttribute("uid"):
                self.connectorviews.append(connectorview)           

        # construct connector instances
        self.connectors = []
        for connectorview in self.connectorviews:
            # don't use ".data" for from or to tags, since they may be alias
            self.connectors.append(Connector(connectorview.getAttribute("uid"),connectorview.getAttribute("angle"),connectorview.getElementsByTagName("from")[0],connectorview.getElementsByTagName("to")[0]))

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
            #print("Constrcting Alias: ", aliasview.getElementsByTagName("of"), "of ", aliasview.getElementsByTagName("of")[0].childNodes[0].data)
            self.aliases.append(Alias(aliasview.getAttribute("uid"),aliasview.getAttribute("x"),aliasview.getAttribute("y"),aliasview.getElementsByTagName("of")[0].childNodes[0].data))

        #print("toal alias", len(self.aliases))
        # now starts the 'drawing' part

        # parameters
        width1 = 46
        height1 = 35
        length1 = 115
        radius1 = 8

        # draw connectors
        for c in self.connectors:
            print("\n")
            print(c.uid)
            # from
            print("c.from_var:", c.from_var,"childNodes:", c.from_var.childNodes)

            if len(c.from_var.childNodes)>1: # if this end is on an alias
                print("it has more than 1 childNodes, so alias")
                from_cord = self.locateAlias(c.from_var.childNodes[1].getAttribute("uid"))
            else:
                print("it has childNodes, so normal variable")
                print("c.from_var.childNodes[0].data: ", c.from_var.childNodes[0].data)
                from_cord = self.locateVar(c.from_var.childNodes[0].data)
            
            print("from_cord: ", from_cord)
            # to
            print("c.to_var", c.to_var, "childNodes:", c.to_var.childNodes)
            if len(c.to_var.childNodes)>1: # if this end is no an alias
                print("it has more than 1 childNodes, so alias")
                to_cord = self.locateAlias(c.to_var.childNodes[1].getAttribute("uid"))
            else:
                print("it has childNodes, so normal variable")
                print("c.to_var.childNodes[0].data: ", c.to_var.childNodes[0].data)
                to_cord = self.locateVar(c.to_var.childNodes[0].data)

            print("to_cord: ", to_cord)
            from_to_cord = from_cord + to_cord
            self.create_connector(from_to_cord[0],from_to_cord[1],from_to_cord[2],from_to_cord[3]-8,c.angle) # minus 8: the arrow it self not consumed
        
        # draw stocks
        for s in self.stocks:
            self.create_stock(s.x, s.y, width1, height1, s.name)
        
        # draw flows
        for f in self.flows:
            self.create_flow(f.x,f.y,f.xA,f.yA,f.xB,f.yB,(pow((f.xB-f.xA),2)+pow((f.yB-f.yA),2)) ** 0.5,radius1,f.name)
        
        # draw auxs
        for a in self.auxs:
            self.create_aux(a.x, a.y, radius1, a.name)

        # draw aliases
        for al in self.aliases:
            self.create_alias(al.x, al.y, radius1, al.of.replace('_',' '))

        self.canvas.pack(fill=tk.BOTH, expand=1)

    def create_stock(self,x,y,w,h,label):
        '''
        Center x, Center y, width, height, label
        '''
        self.canvas.create_rectangle(x-w*0.5, y-h*0.5, x+w*0.5, y+h*0.5, fill="#fff")
        self.canvas.create_text(x,y+30,anchor=tk.CENTER,font=("Arial",9),text=label)

    def create_flow(self, x, y, xA, yA, xB, yB,l,r,label):
        '''
        Starting point x, y, ending point x, y, length, circle radius, label
        '''
        self.canvas.create_line(xA,yA,xB,yB,arrow=tk.LAST)
        self.canvas.create_oval(x-r,y-r,x+r,y+r, fill = "#fff")
        self.canvas.create_text(x,y+r+10,anchor=tk.CENTER,font=("Arial",9),text=label)

    def create_aux(self, x, y, r, label):
        '''
        Central point x, y, radius, label
        '''
        self.canvas.create_oval(x-r,y-r,x+r,y+r,fill="#fff")
        self.canvas.create_text(x,y+r+10,anchor=tk.CENTER,font=("Arial",9),text=label)

    def create_alias(self, x, y, r, label):
        '''
        Central point x, y, radius, label
        '''
        self.canvas.create_oval(x-r,y-r,x+r,y+r,fill="gray70")
        self.canvas.create_text(x,y,anchor=tk.CENTER,font=("Arial",10),text="G")
        self.canvas.create_text(x,y+r+10,anchor=tk.CENTER,font=("Arial",9),text=label)

    def create_connector(self, xA, yA, xB, yB,angle):
        '''
        Starting point x, y, ending point x, y
        '''
        # the last multiplier decides how curvy the link is
        d = (pow((xB-xA),2)+pow((yB-yA),2)) ** 0.5 *0.6
        t1 = math.atan2(yB - yA, xB - xA)
        print("t1, from starting and ending point: ",t1)
        t2 = math.radians(-angle)
        print("t2, from modeler manual adjustment: ",t2)
        if t1 == t2:
            xC = (xA + xB)/2
            yC = (yA + yB)/2
        else:
            xC = (xA + xB)/2 + d * math.sin((t2-t1))
            #xC = (xA + xB)/2 - (yB-yA)/math.sin(t1)/2/math.tan(t2-t1)*math.sin(t2-t1)
            yC = (yA + yB)/2 - d * math.cos((t2-t1))
            #yC = (yA + yB)/2 + (yB-yA)/math.sin(t1)/2/math.tan(t2-t1)*math.cos(t2-t1)

        self.canvas.create_line((xA, yA), (xC, yC), (xB, yB), smooth=True, arrow=tk.LAST, arrowshape=(11,13,4), fill='maroon2')

    def locateVar(self,name):
        name = name.replace("_"," ")
        #print(name)
        for s in self.stocks:
            nameWithoutN = s.name.replace("\\n"," ")
            if nameWithoutN == name:
                return [s.x, s.y]
        for f in self.flows:
            nameWithoutN = f.name.replace("\\n"," ")
            if nameWithoutN == name:
                return [f.x, f.y]
        for a in self.auxs:
            nameWithoutN = a.name.replace("\\n"," ")
            #print(nameWithoutN)
            if nameWithoutN == name:
                return [a.x, a.y]

    def locateAlias(self,uid):
        #print("locateAlias is called")
        for al in self.aliases:
            if al.uid == uid:
                return [al.x, al.y]

def main():

    root = tk.Tk()
    ex = SFDCanvas()
    root.geometry("1280x960+100+100")
    root.mainloop()

if __name__=='__main__':
    main()