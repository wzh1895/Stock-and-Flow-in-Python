"""
main utility for model expansion
"""
from StockAndFlowInPython.SFD_Canvas.SFD_Canvas import SFDCanvas
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import *


class ExpansionPanel(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack(fill=BOTH, expand=1)
        self.sfd_canvas1 = SFDCanvas(self.master)
        self.sfd_canvas1.session_handler1.sess1.first_order_negative()
        self.sfd_canvas1.sfd_drawer()
        self.sfd_canvas1.simulation_handler(simulation_time=80)

        self.simulation_graph = self.sfd_canvas1.session_handler1.sess1.draw_graphs(names=['stock0', 'flow0'], rtn=True)
        self.simulation_figure = FigureCanvasTkAgg(self.simulation_graph, master=self.master)
        self.simulation_figure.draw()
        self.simulation_figure._tkcanvas.pack(side=TOP)

    def test_find_exponential(self):
        pass


def main():
    root = Tk()
    wid = 400
    hei = 1500
    Panel1 = ExpansionPanel(root)
    root.wm_title("Model Expansion")
    root.geometry("%dx%d+100+100" % (wid, hei))
    root.configure(background='#fff')
    root.mainloop()


if __name__ == '__main__':
    main()
