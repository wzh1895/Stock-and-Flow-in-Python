"""
Controller tool bar for this entire project
"""

from tkinter import *
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from StockAndFlowInPython.SFD_Canvas.session_handler import SessionHandler
from StockAndFlowInPython.SFD_Canvas.SFD_Canvas import SFDCanvas


class ControllerBar(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack(fill=BOTH, expand=1)

        self.sfd_window1 = SFDWindow()
        self.graph_network_window1 = GraphNetworkWindow()
        self.simulation_result1 = SimulationResult()

        self.fm_1 = Frame(self.master)
        self.fm_1.pack(side=TOP)
        self.btn1 = Button(self.fm_1, text="Select model", command=self.sfd_window1.sfd_canvas1.file_load)
        self.btn1.pack(side=LEFT)
        self.btn_run = Button(self.fm_1, text="Run", command=self.sfd_window1.sfd_canvas1.simulation_handler)
        self.btn_run.pack(side=LEFT)
        self.comboxlist = ttk.Combobox(self.fm_1)
        self.variables_in_model = ["Variable"]
        self.comboxlist["values"] = self.variables_in_model
        self.comboxlist.current(0)
        self.comboxlist.bind("<<ComboboxSelected>>", self.sfd_window1.sfd_canvas1.select_variable)
        self.comboxlist.pack(side=LEFT)

        self.fm_2 = Frame(self.master)
        self.fm_2.pack(side=TOP)
        self.btn3 = Button(self.fm_2, text="Show Figure", command=self.sfd_window1.sfd_canvas1.show_figure)
        self.btn3.pack(side=LEFT)
        self.btn4 = Button(self.fm_2, text="Reset canvas", command=self.sfd_window1.sfd_canvas1.reset_canvas)
        self.btn4.pack(side=LEFT)
        self.btn5 = Button(self.fm_2, text="Clear a run", command=self.sfd_window1.sfd_canvas1.clear_a_run)
        self.btn5.pack(side=LEFT)

        self.session_handler1 = SessionHandler()
        self.session_handler1.sess1.first_order_negative()
        self.session_handler1.sess1.simulate(simulation_time=80)

        self.simulation_result1.result_figure = FigureCanvasTkAgg(
            self.session_handler1.sess1.draw_results(names=['stock0', 'flow0'], rtn=True),
            master=self.simulation_result1.top
        )
        self.simulation_result1.result_figure._tkcanvas.pack(side=TOP)

        self.graph_network_window1.graph_figure = FigureCanvasTkAgg(
            self.session_handler1.sess1.draw_graphs(rtn=True),
            master=self.graph_network_window1.top
        )
        self.graph_network_window1.graph_figure._tkcanvas.pack(side=TOP)


class SFDWindow(object):
    def __init__(self):
        self.top = Toplevel()
        self.top.title("Stock and Flow Diagram")
        self.top.geometry("%dx%d+700+100" % (500, 500))
        self.sfd_canvas1 = SFDCanvas(self.top)



class GraphNetworkWindow(object):
    def __init__(self):
        self.top = Toplevel()
        self.top.title("Graph Network Structure")
        self.top.geometry("%dx%d+100+300" % (500, 500))


class SimulationResult(object):
    def __init__(self):
        self.top = Toplevel()
        self.top.title("Simulation Result")
        self.top.geometry("%dx%d+400+200" % (500, 500))


def main():
    root = Tk()
    wid = 400
    hei = 60
    controller_bar1 = ControllerBar(root)
    root.wm_title("Controller")
    root.geometry("%dx%d+100+100" % (wid, hei))
    root.configure(background='#fff')
    root.mainloop()


if __name__ == '__main__':
    main()

