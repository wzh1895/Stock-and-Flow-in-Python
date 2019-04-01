"""
main utility for model expansion
"""
from SFD_Canvas.SFD_Canvas import SFDCanvas
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import *


class ExpansionPanel(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack(fill=BOTH, expand=1)
        self.sfd_canvas1 = SFDCanvas(self.master)
        self.sfd_canvas1.session_handler1.sess1.first_order_negative()
        self.sfd_canvas1.model_drawer()
        self.sfd_canvas1.session_handler1.sess1.simulate(simulation_time=80)

        self.simulation_graph = self.sfd_canvas1.session_handler1.sess1.draw_graphs(names=['stock0', 'flow0'], rtn=True)
        self.simulation_figure = FigureCanvasTkAgg(self.simulation_graph, master=self.master)
        self.simulation_figure.draw()
        self.simulation_figure._tkcanvas.pack(side=TOP)


def main():
    root = Tk()
    wid = 500
    hei = 1500
    Panel1 = ExpansionPanel(root)
    root.wm_title("Model Expansion")
    root.geometry("%dx%d+100+100" % (wid, hei))
    root.configure(background='#fff')
    root.mainloop()


if __name__ == '__main__':
    main()
