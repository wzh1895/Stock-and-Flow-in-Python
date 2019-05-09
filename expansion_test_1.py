from tkinter import *
from tkinter import filedialog
from controller_bar import ControllerBar
from StockAndFlowInPython.graph_sd.graph_based_engine import STOCK, FLOW, VARIABLE, PARAMETER, CONNECTOR, ALIAS, \
    MULTIPLICATION, LINEAR
import pandas as pd
import numpy as np


class ExpansionTest(ControllerBar):
    def __init__(self, master):
        super().__init__(master)

        # Expansion
        self.fm_expansion = Frame(self.master)
        self.fm_expansion.pack(side=TOP)
        self.btn_start_expansion = Button(self.fm_expansion, text="Start expansion", command=self.expansion_test)
        self.btn_start_expansion.pack(side=LEFT)

        # Reference modes
        self.reference_mode_path = './StockAndFlowInPython/case/linear_decrease.csv'
        self.numerical_data = None
        self.time_series = dict()
        self.reference_modes = dict()

        self.full_procedure()

    def get_reference_mode_file_name(self):
        self.reference_mode_path = filedialog.askopenfilename()

    def add_reference_mode(self):
        """
        The logic is: file -> file in memory (numerical data) -> time series --selection--> reference mode
        :return:
        """
        if self.reference_mode_path is None and len(self.time_series) == 0:  # either path not specified and no t-series
            self.get_reference_mode_file_name()
        self.numerical_data = pd.read_csv(self.reference_mode_path)
        for column in self.numerical_data:
            self.time_series[column] = np.array(self.numerical_data[column].tolist()).reshape(-1, 1)
        s = SelectReferenceMode(self.time_series)


        #var_name, var_type, ref_obj
        #self.reference_modes[var_name] = [var_type, ref_obj]
        #print("Added reference mode for {} : {}".format(var_type, var_name))

    def full_procedure(self):
        # Show graph/diagram windows
        self.session_handler1.show_sfd_window()
        self.session_handler1.show_graph_network_window()
        # Load a reference mode
        self.add_reference_mode()
        # Build a stock
        self.session_handler1.build_stock(name='stock0', initial_value=100)

    def expansion_test(self):
        self.session_handler1.show_sfd_window()
        self.session_handler1.show_graph_network_window()
        self.session_handler1.build_stock(name='stock0', initial_value=100)
        self.session_handler1.build_flow(name='flow0', equation=4, flow_from='stock0')

        # self.simulate()


class SelectReferenceMode(Toplevel):
    def __init__(self, time_series):
        super().__init__()
        self.title("Select Reference Mode...")
        self.geometry("%dx%d+560+550" % (600, 430))

        time_series_list = Listbox(self)
        for i in range(len(time_series.keys())):
            time_series_list.insert(i, list(time_series.keys())[i])
        time_series_list.pack()


def main():
    root = Tk()
    ExpansionTest(root)
    root.wm_title("Expansion Test")
    root.configure(background='#fff')
    root.mainloop()


if __name__ == '__main__':
    main()
