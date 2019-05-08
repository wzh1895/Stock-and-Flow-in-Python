from tkinter import *
from tkinter import ttk
from StockAndFlowInPython.session_handler import SessionHandler
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from StockAndFlowInPython.similarity_calculation.similarity_calc import SimilarityCalculator
from StockAndFlowInPython.graph_sd.graph_based_engine import STOCK, FLOW, VARIABLE, PARAMETER, CONNECTOR, ALIAS, \
    MULTIPLICATION, LINEAR
import pandas as pd
import numpy as np


class ControllerBar(Frame):
    """
    Controller tool bar for this entire project
    """
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack(fill=BOTH, expand=1)

        self.session_handler1 = SessionHandler()

        self.lb_name = Label(self.master, text='System Dynamics Model', background="#fff")
        self.lb_name.pack(side=TOP)
        self.fm_controller1 = Frame(self.master)
        self.fm_controller1.pack(side=TOP)
        self.btn_load_model = Button(self.fm_controller1, text="Load model", command=self.file_load)
        self.btn_load_model.pack(side=LEFT)
        self.btn_run = Button(self.fm_controller1, text="Simulate", command=self.simulate)
        self.btn_run.pack(side=LEFT)
        self.variables_list = ttk.Combobox(self.fm_controller1)
        self.variables_in_model = ["Variable"]
        self.variables_list["values"] = self.variables_in_model
        self.variables_list.current(0)
        self.variables_list.bind("<<ComboboxSelected>>", self.select_variable)
        self.variables_list.pack(side=LEFT)
        self.sim_time = StringVar()
        self.sim_time.set("20")
        self.entry1 = Entry(self.fm_controller1, width=10, textvariable=self.sim_time)
        self.entry1.pack()

        self.fm_controller2 = Frame(self.master)
        self.fm_controller2.pack(side=TOP)
        self.btn_show_result = Button(self.fm_controller2, text="Show result", command=self.session_handler1.show_result)
        self.btn_show_result.pack(side=LEFT)
        self.btn_reset = Button(self.fm_controller2, text="Reset", command=self.session_handler1.reset)
        self.btn_reset.pack(side=LEFT)
        self.btn_clear_run = Button(self.fm_controller2, text="Clear a run", command=self.session_handler1.clear_a_run)
        self.btn_clear_run.pack(side=LEFT)
        self.btn_refresh = Button(self.fm_controller2, text="Refresh", command=self.session_handler1.refresh)
        self.btn_refresh.pack(side=LEFT)

        # Suggestion

        self.reference_mode_path = './StockAndFlowInPython/case/tea_cup_model.csv'
        # self.reference_mode_path = './StockAndFlowInPython/case/bank_account_model.csv'
        self.similarity_calculator1 = SimilarityCalculator()

        self.fm_suggestion = Frame(self.master)
        self.fm_suggestion.pack(side=TOP)
        self.btn_load_reference_mode = Button(self.fm_suggestion, text="Load reference Mode",
                                              command=self.load_reference_mode)
        self.btn_load_reference_mode.pack(side=LEFT)
        self.btn_calculate_similarity = Button(self.fm_suggestion, text="Calculate similarity",
                                               command=self.calculate_similarity)
        self.btn_calculate_similarity.pack(side=LEFT)
        self.btn_load_generic_structure = Button(self.fm_suggestion, text="Load closest structure",
                                                 command=self.load_generic_structure)
        self.btn_load_generic_structure.pack(side=LEFT)
        self.lb_suggested_generic_stucture = Label(self.master, text="Reference mode pattern", background='#fff')
        self.lb_suggested_generic_stucture.pack(side=TOP)

        # Expansion

        self.fm_expansion = Frame(self.master)
        self.fm_expansion.pack(side=TOP)
        self.btn_start_expansion = Button(self.fm_expansion, text="Start expansion", command=self.expansion_test)
        self.btn_start_expansion.pack(side=LEFT)

        self.expansion_test()

    def expansion_test(self):
        self.session_handler1.show_sfd_window()
        self.session_handler1.show_graph_network_window()
        self.session_handler1.build_stock(name='var1', initial_value=100,
                         # x=289,
                         # y=145
                         )
        self.session_handler1.build_stock(name='var2', initial_value=1)
        self.session_handler1.build_aux(name='fraction0', equation=0.01)
        self.session_handler1.build_aux(name='factor0', equation=[MULTIPLICATION, ['var1', 50], ['var2', 150]])
        self.session_handler1.build_flow(name='flow0', equation=[MULTIPLICATION, ['factor0', 90], ['fraction0', 10]], flow_from='var1', flow_to='var2'
                        # x=181,
                        # y=145,
                        # points=[(85, 145), (266.5, 145)]
                        )
        # self.session_handler1.build_aux(name='fraction0', equation=0.1,
        #                # x=163,
        #                # y=251
        #                )
        # self.session_handler1.build_flow(name='outflow0', equation=5, flow_from='stock0')
        # self.session_handler1.replace_equation(name='outflow0', new_equation=[MULTIPLICATION, ['stock0', 100], ['fraction0', 150]])
        # self.session_handler1.disconnect_stock_flow(flow_name='inflow0', stock_name='stock0')
        # self.session_handler1.disconnect_stock_flow(flow_name='outflow0', stock_name='stock0')
        # self.session_handler1.connect_stock_flow(flow_name='outflow0', new_flow_from='stock0')
        # self.session_handler1.build_aux(name='fraction1', equation=0.1, )
        # self.session_handler1.connect_stock_flow(flow_name='inflow0', new_flow_to='stock0')
        # self.session_handler1.replace_equation(name='inflow0', new_equation=[MULTIPLICATION, ['stock0', 50], ['fraction1', 40]])
        # self.session_handler1.delete_variable(name='inflow0')
        # self.session_handler1.delete_variable(name='fraction1')
        # self.simulate()

    def simulate(self):
        self.session_handler1.simulation_handler(simulation_time=int(self.entry1.get()))
        self.variables_list['values'] = self.session_handler1.variables_in_model

    def file_load(self):
        file_name_and_variables = self.session_handler1.file_load()
        print(file_name_and_variables)
        file_name = file_name_and_variables[0]
        variables_in_model = file_name_and_variables[1]
        print("variables in model:", variables_in_model)
        print("file name:", file_name)
        if file_name != '':
            self.lb_name.config(text=file_name)
            self.variables_list['values'] = variables_in_model

    def select_variable(self, *args):
        print(self.variables_list.get())
        self.session_handler1.selected_variable = self.variables_list.get()

    def load_reference_mode(self):
        self.reference_mode1 = ReferenceMode(self.reference_mode_path)

    def calculate_similarity(self):
        self.suggested_generic_structure, self.comparison_figure = self.similarity_calculator1.similarity_calc(
            who_compare=self.reference_mode1.time_series,
            compare_with='./StockAndFlowInPython/similarity_calculation/basic_behaviors.csv')
        self.lb_suggested_generic_stucture.config(text="Reference mode pattern: "+self.suggested_generic_structure)
        self.comparison_window1 = ComparisonWindow(self.comparison_figure)

    def load_generic_structure(self):
        self.session_handler1.apply_generic_structure(self.suggested_generic_structure)
        variables_in_model = list(self.session_handler1.sess1.structures['default'].sfd.nodes)
        print("variables in model:", variables_in_model)
        print("structure name:", self.suggested_generic_structure)
        self.lb_name.config(text=self.suggested_generic_structure)
        self.variables_list['values'] = variables_in_model


class ReferenceMode(object):
    """Class for Reference Mode"""
    def __init__(self, filename):
        self.case_numerical_data_filename = filename
        self.case_numerical_data = pd.read_csv(self.case_numerical_data_filename)
        self.time_series = np.array(self.case_numerical_data["tea-cup"].tolist()).reshape(-1, 1)
        #self.time_series = np.array(self.case_numerical_data["balance"].tolist()).reshape(-1, 1)
        #self.reference_mode_window1 = ReferenceModeWindow(time_series=self.time_series, time_series_name="Accoutn balance")
        self.reference_mode_window1 = ReferenceModeWindow(time_series=self.time_series,
                                                          time_series_name="Tea-cup Temperature")


class ComparisonWindow(object):
    def __init__(self, comparison_figure):
        self.top = Toplevel()
        self.top.title("Comparison with Generic Behaviors")
        self.top.geometry("%dx%d+560+550" % (500, 430))
        self.comparison_graph = FigureCanvasTkAgg(comparison_figure, master=self.top)
        self.comparison_graph.draw()
        self.comparison_graph.get_tk_widget().pack(side=TOP)


class ReferenceModeWindow(object):
    def __init__(self, time_series, time_series_name):
        self.top = Toplevel()
        self.top.title("Reference Mode")
        self.top.geometry("%dx%d+50+550" % (500, 430))
        self.reference_mode_figure = Figure(figsize=(5, 4))
        self.reference_mode_plot = self.reference_mode_figure.add_subplot(111)
        self.reference_mode_plot.plot(time_series, '*')
        self.reference_mode_plot.set_xlabel("Time")
        self.reference_mode_plot.set_ylabel(time_series_name)
        self.reference_mode_graph = FigureCanvasTkAgg(self.reference_mode_figure, master=self.top)
        self.reference_mode_graph.draw()
        self.reference_mode_graph.get_tk_widget().pack(side=TOP)


def main():
    root = Tk()
    ControllerBar(root)
    root.wm_title("Controller")
    root.geometry("%dx%d+50+100" % (485, 160))
    root.configure(background='#fff')
    root.mainloop()


if __name__ == '__main__':
    main()
