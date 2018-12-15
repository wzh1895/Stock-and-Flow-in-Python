from flexx import flx, event

class DisplayArea(flx.CanvasWidget):

    # CSS's name should match the pattern "flx-$Classname"

    CSS = """
        .flx-DisplayArea {background: #fff; border: 5px solid #888;}
        """

    def init(self):
        super().init()
        self.ctx = self.node.getContext('2d')


class SFDCanvas(flx.Widget):
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
            self.display = DisplayArea(flex=1)

app = flx.App(SFDCanvas)

#app.export('example.html', link=0)  # Export to single file
#app.launch('browser')  # show it now in a browser
#flx.run()  # enter the mainloop

app.serve('')
flx.start()
