from flexx import flx, event

from modelHandler import ModelHandler

filename = "reindeerModel.stmx"
modelHandler1 = ModelHandler(filename)

class DisplayArea(flx.CanvasWidget):
    # CSS's name should match the pattern "flx-$Classname"

    CSS = """
        .flx-DisplayArea {background: #fff; border: 5px solid #888;}
        """

    def init(self):
        self.ctx = self.node.getContext('2d')
        self.connectors = []
        self.stocks = []
        self.flows = []
        self.auxs = []
        self.aliases = []

    @flx.reaction('size')  # react to 'size' event: every time canvas gets sized (or resized), this function executes.
    def diagramUpdate(self):
        '''Update all diagrams on Canvas'''
        '''Draw stocks'''
        self.create_stock(50, 60, 46, 35,"Stock 1")
        '''Draw flows'''
        '''Draw auxes'''
        '''Draw ghosts'''
        '''Dras connectors'''

    def create_stock(self, x, y, w, h, label):
        '''
        Center x, Center y, width, height, label
        '''
        self.ctx.strokeStyle = "black"
        self.ctx.lineWidth = "2"
        self.ctx.strokeRect(x - w * .05, y - h * 0.5, w, h)
        self.ctx.fillText(label, x, y + 30)

    '''
    def modelDrawer(self):
        # now starts the 'drawing' part

        # set common parameters
        width1 = 46
        height1 = 35
        length1 = 115
        radius1 = 5

        # draw connectors
        for c in self.modelHandler1.connectors:
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
        for s in self.modelHandler1.stocks:
            self.create_stock(s.x, s.y, width1, height1, s.name)
            if s.x> self.xmost:
                self.xmost = s.x
            if s.y> self.ymost:
                self.ymost = s.y

        # draw flows
        for f in self.modelHandler1.flows:
            self.create_flow(f.x, f.y, f.pts, radius1, f.name)
            if f.x > self.xmost:
                self.xmost = f.x
            if f.y > self.ymost:
                self.ymost = f.y

        # draw auxs
        for a in self.modelHandler1.auxs:
            self.create_aux(a.x, a.y, radius1, a.name)
            if a.x > self.xmost:
                self.xmost = a.x
            if a.y > self.ymost:
                self.ymost = a.y

        # draw aliases
        for al in self.modelHandler1.aliases:
            self.create_alias(al.x, al.y, radius1, al.of.replace('_', ' '))
            if al.x > self.xmost:
                self.xmost = al.x
            if al.y > self.ymost:
                self.ymost = al.y

        self.xmost += 150
        self.ymost += 100
        #print('Xmost,',self.xmost,'Ymost,',self.ymost)
    '''


class MainWidget(flx.Widget):
    def init(self):
        self.variablesInModel = ["Variable"]

        with flx.VBox(flex=1):
            with flx.HBox():
                flx.Label(text='Load and display a Stella SD Model')
            with flx.HBox():
                flx.Button(text='Select model')
                flx.Button(text='Run')
                flx.ComboBox(options=self.variablesInModel, selected_index=0, style='width: 100%')
                flx.Button(text='Show figure')
                flx.Button(text='Reset canvas')
            self.displayArea = DisplayArea(flex=1)

app = flx.App(MainWidget)

# app.export('example.html', link=0)  # Export to single file
# app.launch('')  # show it now in a browser
# flx.run()  # enter the mainloop

app.serve('')
flx.start()
