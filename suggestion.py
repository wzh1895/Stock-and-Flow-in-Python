"""
main utility for generic structure suggestion
"""
from tkinter import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from controller import ControllerBar
from StockAndFlowInPython.similarity_calculation.similarity_calc import SimilarityCalculator
import pandas as pd
import numpy as np


class SuggestionPanel(ControllerBar):
    def __init__(self, master):
        super().__init__(master)
        self.load_reference_mode('./StockAndFlowInPython/case/tea_cup_model.csv')
        self.similarity_calculator1 = SimilarityCalculator()
        self.suggested_generic_structure = self.similarity_calculation()
        self.load_generic_structure()

    def load_generic_structure(self):
        self.session_handler1.generic_structure_load(self.suggested_generic_structure)
        variables_in_model = list(self.session_handler1.sess1.structures['default'].sfd.nodes)
        print("variables in model:", variables_in_model)
        print("structure name:", self.suggested_generic_structure)
        self.lb.config(text=self.suggested_generic_structure)
        self.comboxlist['values'] = variables_in_model


    def load_reference_mode(self, reference_mode_file_name):
        self.reference_mode1 = ReferenceMode(reference_mode_file_name)

    def similarity_calculation(self):
        suggested_generic_structure, comparison_figure = self.similarity_calculator1.similarity_calc(
            who_compare=self.reference_mode1.tea_cup_temperature_time_series,
            compare_with='./StockAndFlowInPython/similarity_calculation/basic_behaviors.csv')
        self.comparison_window1 = ComparisonWindow(comparison_figure)
        return suggested_generic_structure


class ReferenceMode(object):
    """Class for Reference Mode"""
    def __init__(self, filename):
        self.case_numerical_data_filename = filename
        self.case_numerical_data = pd.read_csv(self.case_numerical_data_filename)
        self.tea_cup_temperature_time_series = np.array(self.case_numerical_data["tea-cup"].tolist()).reshape(-1, 1)
        self.reference_mode_window1 = ReferenceModeWindow(self.tea_cup_temperature_time_series)


class ComparisonWindow(object):
    def __init__(self, comparison_figure):
        self.top = Toplevel()
        self.top.title("Comparison with Generic Behaviors")
        self.top.geometry("%dx%d+560+550" % (500, 430))
        self.comparison_graph = FigureCanvasTkAgg(comparison_figure, master=self.top)
        self.comparison_graph.draw()
        self.comparison_graph.get_tk_widget().pack(side=TOP)
        #self.comparison_plot = self.comparison_figure.add_subplot(111)
        #self.comparison_plot.set_xlabel("Time")
        #self.comparison_plot.set_ylabel("Behavior")
        #self.comparison_graph =


class ReferenceModeWindow(object):
    def __init__(self, time_series):
        self.top = Toplevel()
        self.top.title("Reference Mode")
        self.top.geometry("%dx%d+50+550" % (500, 430))
        self.reference_mode_figure = Figure(figsize=(5, 4))
        self.reference_mode_plot = self.reference_mode_figure.add_subplot(111)
        self.reference_mode_plot.plot(time_series, '*')
        self.reference_mode_plot.set_xlabel("Time")
        self.reference_mode_plot.set_ylabel("Tea-cup Temperature")
        self.reference_mode_graph = FigureCanvasTkAgg(self.reference_mode_figure, master=self.top)
        self.reference_mode_graph.draw()
        self.reference_mode_graph.get_tk_widget().pack(side=TOP)


def main():
    root = Tk()
    #suggestion_test1 = ControllerBar(root)
    suggestion_test1 = SuggestionPanel(root)
    root.wm_title("Suggestion Test")
    root.geometry("%dx%d+50+100" % (suggestion_test1.wid, suggestion_test1.hei))
    root.configure(background='#fff')
    root.mainloop()


if __name__ == '__main__':
    main()
