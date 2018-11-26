from flexx import flx

class Example(flx.Widget):
    def init(self):
        flx.Label(text='Load and display a Stella SD Model')
        self.variablesInModel = ["Variable"]
        with flx.HBox():
            flx.Button(text='Select model')
            flx.Button(text='Run')
            flx.ComboBox(options=self.variablesInModel, selected_index=0, style='width: 100%')
            flx.Button(text='Show figure')
            flx.Button(text='Reset canvas')

app = flx.App(Example)

#app.export('example.html', link=0)  # Export to single file
#app.launch('browser')  # show it now in a browser
#flx.run()  # enter the mainloop

app.serve('')
flx.start()
