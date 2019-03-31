"""
Main function of the program
"""

from matplotlib.figure import Figure
from tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from similarity_calculation.similarity_calc import similarity_calc
from SFD_Canvas.SFD_Canvas import SFDCanvas
import numpy as np
import pandas as pd


class Panel(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.fm_1 = LabelFrame(self.master, text='Problem', width=500, background='#fff')
        self.fm_1.propagate(False)  # Prevent the labelframe from shrinking when a label is placed in it.
        self.lb1 = Label(self.fm_1, text='Reference Mode:', anchor='nw', background='#fff')
        self.lb1.pack(side=TOP)
        self.fm_1.pack(side=LEFT, fill=BOTH, expand=YES)

        self.fm_2 = LabelFrame(self.master, text='Hypothesis', width=500, background='#fff')
        self.fm_2.propagate(False)
        self.lb2 = Label(self.fm_2, text='Compare reference mode with known modes:', anchor='nw', background='#fff')
        self.lb2.pack(side=TOP)
        self.fm_2.pack(side=LEFT, fill=BOTH, expand=YES)

        self.fm_3 = LabelFrame(self.master, text='Analysis', width=500, background='#fff')
        self.fm_3.propagate(False)
        self.fm_3.pack(side=LEFT, fill=BOTH, expand=YES)

        self.pack(fill=BOTH, expand=1)

        # Load reference mode of the case and show

        self.case_numerical_data_filename = './case/tea_cup_model.csv'
        self.case_numerical_data = pd.read_csv(self.case_numerical_data_filename)

        self.tea_cup_temperature_time_series = np.array(self.case_numerical_data["tea-cup"].tolist()).reshape(-1, 1)
        self.reference_mode_figure = Figure(figsize=(5, 4), dpi=75)
        self.reference_mode_plot = self.reference_mode_figure.add_subplot(111)
        self.reference_mode_plot.plot(self.tea_cup_temperature_time_series, '*')
        self.reference_mode_plot.set_xlabel("Time")
        self.reference_mode_plot.set_ylabel("Tea-cup Temperature")
        self.reference_mode_graph = FigureCanvasTkAgg(self.reference_mode_figure, master=self.fm_1)
        self.reference_mode_graph.draw()
        self.reference_mode_graph._tkcanvas.pack(side=TOP)

        # Calculate similarity and suggest archetype

        self.suggested_archetype, self.comparison_figure = similarity_calc(self.tea_cup_temperature_time_series)
        # print(dir(self.comparison_figure.get_axes()[0]))
        # self.comparison_figure.get_axes()[0].axis('off')  # disable axes
        self.comparison_figure.get_axes()[0].set_xticks([])  # disable ticks on X-axis
        self.comparison_graph = FigureCanvasTkAgg(self.comparison_figure, master=self.fm_2)
        self.comparison_graph.draw()
        self.comparison_graph._tkcanvas.pack(side=TOP)
        self.lb3 = Label(self.fm_2, text='Reference mode is classified as:', background='#fff')
        self.lb3.pack(side=TOP)
        self.lb4 = Label(self.fm_2, text=self.suggested_archetype+'\n', font='Helvetica 16 bold', background='#fff')
        self.lb4.pack(side=TOP)
        self.lb5 = Label(self.fm_2, text='Suggesting the following structure:', background='#fff')
        self.lb5.pack(side=TOP)

        # Load archetype(s) based on similarity and draw the suggested archetype with SFDCanvas
        self.sfd_canvas1 = SFDCanvas(self.fm_2)
        if self.suggested_archetype == 'decline_c':
            self.sfd_canvas1.session_handler1.sess1.first_order_negative()
            self.sfd_canvas1.model_drawer()

        # Run the model
        self.sfd_canvas1.session_handler1.sess1.simulate(simulation_time=80)
        self.lb6 = Label(self.fm_3, text='The suggested structure simulates as follows:', background='#fff')
        self.lb6.pack(side=TOP)
        # Use rtn=True to ask the engine to return the graph, instead of drawing it by itself.
        self.simulation_graph = self.sfd_canvas1.session_handler1.sess1.draw_graphs(names=['stock0', 'flow0'], rtn=True)
        self.simulation_figure = FigureCanvasTkAgg(self.simulation_graph, master=self.fm_3)
        self.simulation_figure.draw()
        self.simulation_figure._tkcanvas.pack(side=TOP)


if __name__ == '__main__':
    root = Tk()
    wid = 1500
    hei = 800
    root.wm_title("Conceptualization Panel")
    root.geometry("%dx%d+100+100" % (wid, hei))
    root.configure(background='white')
    Panel = Panel(root)
    root.mainloop()
