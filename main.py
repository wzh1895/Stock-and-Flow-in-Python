"""
Main function of the program
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import *

from similarityCalc import similarity_calc
from sdClasses import Stock, Flow, Aux, Time
import globalModel as glbele

glbele._init()


def first_order_negative():

    glbele.set_value('stock1', Stock(name='stock1', x=489, y=245, eqn=str(100), inflow='flow1'))
    glbele.set_value('flow1', Flow(name='flow1', x=381.75, y=245, pts=[(285, 245), (466.5, 245)],
                                   eqn="(globalModel.get_value('goal1')()-globalModel.get_value('stock1')())/globalModel.get_value('at1')()"))
    glbele.set_value('at1', Aux(name='at1', x=341.5, y=156.5, eqn=str(5)))
    glbele.set_value('goal1', Aux(name='goal1', x=348, y=329, eqn=str(1)))

    glbele.set_value('time1', Time(end=25, start=1, dt=0.125))


behavior_to_archetype = {'decline_c':first_order_negative()}


class Panel(Frame):
    def __init__(self,master):
        super().__init__(master)
        self.master = master

        self.fm_1 = LabelFrame(self.master, text='Problem', width=400)
        self.fm_1.propagate(False)  # Prevent the labelframe from shrinking when a label is placed in it.
        self.lb1 = Label(self.fm_1, text='Reference Mode:', anchor='nw')
        self.lb1.pack(side=TOP)
        self.fm_1.pack(side=LEFT, fill=BOTH, expand=YES)

        self.fm_2 = LabelFrame(self.master, text='Hypothesis', width=400)
        self.fm_2.propagate(False)
        self.lb2 = Label(self.fm_2, text='Comparison with known modes:', anchor='nw')
        self.lb2.pack(side=TOP)
        self.fm_2.pack(side=LEFT, fill=BOTH, expand=YES)

        self.fm_3 = LabelFrame(self.master, text='Analysis', width=400)
        self.fm_3.propagate(False)
        self.canvas = Canvas(self)
        self.canvas.pack(side=TOP)
        self.fm_3.pack(side=LEFT, fill=BOTH, expand=YES)

        self.pack(fill=BOTH, expand=1)

        # Load reference mode of the case and show

        self.case_numerical_data_filename = './case/tea_cup_model.csv'
        self.case_numerical_data = pd.read_csv(self.case_numerical_data_filename)

        self.tea_cup_temperature_time_series = np.array(self.case_numerical_data["tea-cup"].tolist()).reshape(-1, 1)
        self.reference_mode_figure = Figure(figsize=(5, 4), dpi=75)
        self.reference_mode_plot = self.reference_mode_figure.add_subplot(111)
        self.reference_mode_plot.plot(self.tea_cup_temperature_time_series)
        self.reference_mode_plot.set_xlabel("Time")
        self.reference_mode_plot.set_ylabel("Tea-cup Temperature")
        self.reference_mode_graph = FigureCanvasTkAgg(self.reference_mode_figure, master=self.fm_1)
        self.reference_mode_graph.draw()
        self.reference_mode_graph._tkcanvas.pack(side=TOP)

        # Calculate similarity and suggest archetype

        self.suggested_archetype, self.comparison_figure = similarity_calc(self.tea_cup_temperature_time_series)
        self.comparison_graph = FigureCanvasTkAgg(self.comparison_figure, master=self.fm_2)
        self.comparison_graph.draw()
        self.comparison_graph._tkcanvas.pack(side=TOP)
        self.lb3 = Label(self.fm_2, text='Reference mode is classified as:\n'+self.suggested_archetype)
        self.lb3.pack(side=TOP)

        '''
        # Load archetype(s) based on similarity

        behavior_to_archetype[suggested_archetype]

        # Generate lists of flows and stocks

        flows = {}
        stocks = []
        for element in glbele.get_keys():
            if type(glbele.get_value(element)) == Flow:
                flows[element] = 0
            if type(glbele.get_value(element)) == Stock:
                stocks.append(element)

        # Run the model

        for step in range(glbele.get_value('time1').steps):
            print('After step: ', step)

            # 1. Calculate all flows as recursion, which trace back to stocks or exogenous params.
            for flow in flows:
                flows[flow] = glbele.get_value(flow)()
                print(flow, flows[flow])

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

        #plt.plot(glbele.get_value('stock1').behavior)
        #plt.show()
        '''
if __name__ == '__main__':
    root = Tk()
    wid = 1200
    hei = 800
    root.wm_title("Conceptualization Panel")
    root.geometry(str(wid)+"x"+str(hei)+"+100+100")
    Panel = Panel(root)
    root.mainloop()
