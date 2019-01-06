"""
Main function of the program
"""

import numpy as np
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from tkinter import *

from similarityCalc import similarity_calc
from globalModel import Stock, Flow, Aux, Time, Connector
import globalModel as glbele
from SFDDisplay import SFDCanvas

glbele._init()


def first_order_negative():

    glbele.set_value('stock1', Stock(name='stock1', x=289, y=145, eqn=str(100), inflow='flow1'))
    glbele.set_value('flow1', Flow(name='flow1', x=181.75, y=145, pts=[(85, 145), (266.5, 145)],
                                   eqn="(get_value('goal1')()-get_value('stock1')())/get_value('at1')()"))
    glbele.set_value('at1', Aux(name='at1', x=141.5, y=56.5, eqn=str(5)))
    glbele.set_value('goal1', Aux(name='goal1', x=148, y=229, eqn=str(1)))

    glbele.set_value('time1', Time(end=25, start=1, dt=0.125))

    glbele.set_value('1', Connector(1, 150, 'stock1', 'flow1'))
    glbele.set_value('2', Connector(2, 300, 'at1', 'flow1'))
    glbele.set_value('3', Connector(3, 60, 'goal1', 'flow1'))

# a dict mapping behavior name to the loading of corresponding archetype


behavior_to_archetype = {'decline_c':first_order_negative()}


class Panel(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        self.fm_1 = LabelFrame(self.master, text='Problem', width=400)
        self.fm_1.propagate(False)  # Prevent the labelframe from shrinking when a label is placed in it.
        self.lb1 = Label(self.fm_1, text='Reference Mode:', anchor='nw')
        self.lb1.pack(side=TOP)
        self.fm_1.pack(side=LEFT, fill=BOTH, expand=YES)

        self.fm_2 = LabelFrame(self.master, text='Hypothesis', width=400)
        self.fm_2.propagate(False)
        self.lb2 = Label(self.fm_2, text='Compare reference mode with known modes:', anchor='nw')
        self.lb2.pack(side=TOP)
        self.fm_2.pack(side=LEFT, fill=BOTH, expand=YES)

        self.fm_3 = LabelFrame(self.master, text='Analysis', width=400)
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
        self.lb3 = Label(self.fm_2, text='Reference mode is classified as:')
        self.lb3.pack(side=TOP)
        self.lb4 = Label(self.fm_2, text=self.suggested_archetype+'\n', font='Helvetica 16 bold')
        self.lb4.pack(side=TOP)
        self.lb5 = Label(self.fm_2, text='Suggesting the following structure:')
        self.lb5.pack(side=TOP)

        # Load archetype(s) based on similarity

        behavior_to_archetype[self.suggested_archetype]

        # Draw the suggested archetype on with SFDCanvas

        self.sfd_canvas1 = SFDCanvas(self.fm_2, stocks=glbele.get_stocks(), flows=glbele.get_flows(), auxs=glbele.get_auxs(), connectors=glbele.get_connectors())

        
        # Generate lists of flows and stocks

        flows = {}  # use a dictionary to store both flow names and their values
        stocks = []
        for element in glbele.get_keys():
            if type(glbele.get_value(element)) == Flow:
                flows[element] = 0
            if type(glbele.get_value(element)) == Stock:
                stocks.append(element)


        # Run the model

        for step in range(glbele.get_value('time1').steps):
            # print('After step: ', step)

            # 1. Calculate all flows as recursion, which trace back to stocks or exogenous params.
            for flow in flows:
                flows[flow] = glbele.get_value(flow)()
                # print(flow, flows[flow])

            # 2. Change stocks with flows
            for stock in stocks:
                try:
                    glbele.get_value(stock).change_in_stock(flows[glbele.get_value(stock).inflow]*glbele.get_value('time1').dt)
                except:
                    pass
                try:
                    glbele.get_value(stock).change_in_stock(flows[glbele.get_value(stock).outflow]*glbele.get_value('time1').dt*(-1))
                except:
                    pass

            glbele.get_value('time1').current_step += 1

        self.lb6 = Label(self.fm_3, text='The suggested structure simulates as follows:')
        self.lb6.pack(side=TOP)

        self.simulation_figure = Figure(figsize=(5, 4), dpi=75)
        self.simulation_plot = self.simulation_figure.add_subplot(111)
        self.simulation_plot.plot(glbele.get_value('stock1').behavior)
        self.simulation_plot.set_xlabel("Time")
        self.simulation_plot.set_ylabel("stock1")
        self.simulation_graph = FigureCanvasTkAgg(self.simulation_figure, master=self.fm_3)
        self.simulation_graph.draw()
        self.simulation_graph._tkcanvas.pack(side=TOP)


if __name__ == '__main__':
    root = Tk()
    wid = 1200
    hei = 800
    root.wm_title("Conceptualization Panel")
    root.geometry(str(wid)+"x"+str(hei)+"+100+100")
    Panel = Panel(root)
    root.mainloop()
