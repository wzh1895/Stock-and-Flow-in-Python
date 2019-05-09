from tkinter import *
from tkinter import filedialog
from controller_bar import ControllerBar
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
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
        #self.reference_mode_path = './StockAndFlowInPython/case/linear_decrease.csv'
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
        select_dialog = SelectReferenceMode(self.time_series)
        self.wait_window(select_dialog)  # important!
        reference_mode_type = select_dialog.reference_mode_type
        reference_mode_name = select_dialog.selected_reference_mode
        if reference_mode_type is not None and reference_mode_name is not None:
            self.reference_modes[reference_mode_name] = [reference_mode_type, self.time_series[reference_mode_name]]
            print("Added reference mode for {} : {}".format(reference_mode_type, reference_mode_name))

    def full_procedure(self):
        # Show graph/diagram windows
        self.session_handler1.show_sfd_window()
        self.session_handler1.show_graph_network_window()
        # Load a reference mode
        self.add_reference_mode()
        # Build stock(s)
        for reference_mode in self.reference_modes.keys():
            if self.reference_modes[reference_mode][0] == STOCK:
                self.session_handler1.build_stock(name=reference_mode,
                                                  initial_value=self.reference_modes[reference_mode][1][0])

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
        #self.geometry("%dx%d+100+100" % (600, 430))
        self.time_series = time_series
        self.selected_reference_mode = None
        self.reference_mode_type = None
        self.fm_select = Frame(self)
        self.fm_select.pack(side=LEFT)
        self.time_series_list = Listbox(self.fm_select)
        self.time_series_list.pack(side=TOP)
        for column in time_series.keys():
            self.time_series_list.insert(END, column)
        self.time_series_list.bind('<<ListboxSelect>>', self.display_reference_mode)

        self.ref_md_type = StringVar(self, value='None')
        self.radio_button_type_1 = Radiobutton(self.fm_select, text='Stock', variable=self.ref_md_type, value=STOCK)
        self.radio_button_type_1.pack(side=TOP, anchor='w')
        self.radio_button_type_2 = Radiobutton(self.fm_select, text='Flow', variable=self.ref_md_type, value=FLOW)
        self.radio_button_type_2.pack(side=TOP, anchor='w')
        self.radio_button_type_3 = Radiobutton(self.fm_select, text='Auxiliary', variable=self.ref_md_type, value=VARIABLE)
        self.radio_button_type_3.pack(side=TOP, anchor='w')

        self.fm_display = Frame(self)
        self.fm_display.pack(side=LEFT)

        self.fm_buttons = Frame(self.fm_select)
        self.fm_buttons.pack(side=BOTTOM, anchor='center')
        self.confirm_button = Button(self.fm_buttons, text='Confirm', command=self.confirm)
        self.confirm_button.pack(side=LEFT, anchor='center')
        self.confirm_button = Button(self.fm_buttons, text='Cancel', command=self.cancel)
        self.confirm_button.pack(side=LEFT, anchor='center')

    def display_reference_mode(self, evt):
        try:
            self.reference_mode_graph.get_tk_widget().destroy()
        except AttributeError:
            pass
        self.reference_mode_figure = Figure(figsize=(5, 4))
        self.reference_mode_plot = self.reference_mode_figure.add_subplot(111)
        self.reference_mode_plot.plot(self.time_series[self.time_series_list.get(self.time_series_list.curselection())], '*')
        self.reference_mode_plot.set_xlabel("Time")
        self.reference_mode_plot.set_ylabel(self.time_series_list.get(self.time_series_list.curselection()))
        self.reference_mode_graph = FigureCanvasTkAgg(self.reference_mode_figure, master=self.fm_display)
        self.reference_mode_graph.draw()
        self.reference_mode_graph.get_tk_widget().pack(side=LEFT)

    def confirm(self):
        self.reference_mode_type = self.ref_md_type.get()
        self.selected_reference_mode = self.time_series_list.get(self.time_series_list.curselection())
        self.destroy()

    def cancel(self):
        self.reference_mode_type = None
        self.selected_reference_mode = None
        self.destroy()


def main():
    root = Tk()
    ExpansionTest(root)
    root.wm_title("Expansion Test")
    root.configure(background='#fff')
    root.mainloop()


if __name__ == '__main__':
    main()
