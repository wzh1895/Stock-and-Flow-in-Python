from tkinter import *
from tkinter import filedialog
from controller_bar import ControllerBar, ComparisonWindow, ReferenceModeWindow
from StockAndFlowInPython.session_handler import SessionHandler, SFDWindow, GraphNetworkWindow, NewGraphNetworkWindow
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from StockAndFlowInPython.similarity_calculation.similarity_calc import SimilarityCalculator
from StockAndFlowInPython.graph_sd.graph_based_engine import Session, function_names, STOCK, FLOW, VARIABLE, PARAMETER, CONNECTOR, ALIAS, \
    MULTIPLICATION, LINEAR
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import random
import copy

class ExpansionTest(ControllerBar):
    def __init__(self, master):
        super().__init__(master)

        # Overwriting
        self.btn_load_reference_mode = Button(self.fm_suggestion, text="Load reference Mode",
                                              command=self.load_reference_mode)

        # Expansion
        # self.fm_expansion = Frame(self.master)
        # self.fm_expansion.pack(side=TOP)
        # self.btn_start_expansion = Button(self.fm_expansion, text="Start expansion", command=self.expansion_test)
        # self.btn_start_expansion.pack(side=LEFT)

        # Reference modes
        self.reference_mode_path = './StockAndFlowInPython/case/linear_decrease.csv'
        # self.reference_mode_path = './StockAndFlowInPython/case/tea_cup_model.csv'
        self.numerical_data = None
        self.time_series = dict()
        self.reference_modes = dict()

        # self.full_procedure()

        # Initialize concept CLDs (generic structures)
        self.concept_manager = ConceptManager()

        # Initialize builder rack
        self.possibility_rack = list()

        # Initialize expansion manager
        self.expansion_manager = StructureManager()
        self.expansion_manager.add_structure(structure=0)

        # Load reference mode
        self.load_reference_mode()

        # Display reference mode
        self.reference_mode_window1 = ReferenceModeWindow(self.reference_modes['stock0'][1], 'stock0')

        # Main loop
        random.seed(10)

        # Specify round to iterate
        self.iteration_time = 2
        i = 1
        while i <= self.iteration_time:
            print('Expansion: Iterating {}'.format(i))
            self.expansion_manager.derive_structure(self.expansion_manager.uid-1)
            # print(SimilarityCalculator.similarity_calc(np.array(self.reference_modes['stock0'][1]), np.array(self.concept_clds[0].sess1.get_behavior('stock0'))))
            for concept_cld in self.concept_manager.concept_clds:
                self.behavioral_similarity(who_compare=self.reference_modes['stock0'][1],
                                           compare_with=concept_cld.sess1.get_behavior('stock0'))
            self.expansion_manager.generate_distribution()
            self.expansion_manager.display_tree()
            i += 1

    def generate_possibility(self):
        pass

    def structural_similarity(self):
        pass

    def behavioral_similarity(self, who_compare, compare_with):
        print("Expansion: Calculating similarity...")
        distance, comparison_figure = SimilarityCalculator.similarity_calc(np.array(who_compare).reshape(-1, 1),
                                                    np.array(compare_with).reshape(-1, 1))
        # ComparisonWindow(comparison_figure)
        return distance

    def adjust_concept_cld_likelihood(self):
        pass

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
            self.time_series[column] = self.numerical_data[column].tolist()
        select_dialog = SelectReferenceMode(self.time_series)
        self.wait_window(select_dialog)  # important!
        reference_mode_type = select_dialog.reference_mode_type
        reference_mode_name = select_dialog.selected_reference_mode
        if reference_mode_type is not None and reference_mode_name is not None:
            self.reference_modes[reference_mode_name] = [reference_mode_type, self.time_series[reference_mode_name]]
            print("Added reference mode for {} : {}".format(reference_mode_type, reference_mode_name))

    def load_reference_mode(self):
        self.add_reference_mode()


class ConceptManager(object):
    """The class containing and managing all concept clds"""
    def __init__(self):
        self.concept_clds = list()
        self.concept_clds.append(SessionHandler())
        self.concept_clds[-1].sess1.basic_stock_inflow()
        self.concept_clds[-1].sess1.simulate(simulation_time=25)
        self.concept_clds[-1].sess1.structures['default'].sfd.graph['likelihood'] = 10

        self.concept_clds.append(SessionHandler())
        self.concept_clds[-1].sess1.basic_stock_outflow()
        self.concept_clds[-1].sess1.simulate(simulation_time=25)
        self.concept_clds[-1].sess1.structures['default'].sfd.graph['likelihood'] = 10

        self.concept_clds.append(SessionHandler())
        self.concept_clds[-1].sess1.first_order_positive()
        self.concept_clds[-1].sess1.simulate(simulation_time=25)
        self.concept_clds[-1].sess1.structures['default'].sfd.graph['likelihood'] = 10

        self.concept_clds.append(SessionHandler())
        self.concept_clds[-1].sess1.first_order_negative()
        self.concept_clds[-1].sess1.simulate(simulation_time=25)
        self.concept_clds[-1].sess1.structures['default'].sfd.graph['likelihood'] = 10


    def generate_distribution(self):
        """Generate a list, containing multiple uids of each structure"""
        distribution_list = list()
        for concept_cld in list(self.concept_clds):
            for i in range(concept_cld.sess1.structures['default'].sfd.graph['likelihood']):
                distribution_list.append(concept_cld.sess1.structures['default'].sfd.graph['structure_name'])
        return distribution_list

    # def generate_distribution(self):
    #     """Generate a list, containing multiple uids of each structure"""
    #     distribution_list = list()
    #     for structure in list(self.concept_clds):
    #         for i in range(self.tree.nodes[structure]['activity']):
    #             distribution_list.append(structure)
    #     return distribution_list


class StructureManager(object):
    """The class containing and managing all variants of structures"""
    def __init__(self):
        self.tree = nx.DiGraph()
        self.uid = 0
        self.tree_window = NewGraphNetworkWindow(self.tree)

    def get_uid(self):
        """Get unique id for structure"""
        self.uid += 1
        return self.uid - 1

    def add_structure(self, structure):
        """Add a structure, usually as starting point"""
        self.tree.add_node(self.get_uid(), structure=structure, activity=10)

    def derive_structure(self, base_structure_uid):
        """Derive a new structure from an existing one"""
        # add a new node
        new_uid = self.get_uid()
        self.tree.add_node(new_uid,
                           structure=copy.deepcopy(self.tree.nodes[base_structure_uid]['structure']),
                           activity=self.tree.nodes[base_structure_uid]['activity']
                           )
        # build a link from the old to the new
        self.tree.add_edge(base_structure_uid, new_uid)

    def cool_down(self):
        """Update structures' activity (cooling down) after one iteration"""
        for u in self.tree.nodes:
            self.tree.nodes[u]['activity'] = self.tree.nodes[u]['activity'] - 1

    def random_single(self):
        """Return one structure"""
        return random.choice(self.generate_distribution())

    def random_pair(self):
        """Return a pair of structures for competition"""
        return random.choices(self.generate_distribution(), k=2)

    def update_activity_elo(self, winner, loser):
        """Update winner and loser's activity using Elo Rating System"""
        r_winner = self.tree.nodes[winner]['activity']
        r_loser = self.tree.nodes[loser]['activity']
        e_winner = 1/(1+10**((r_loser-r_winner)/400))
        e_loser = 1/(1+10**((r_winner-r_loser)/400))
        gain_winner = 1
        gain_loser = 0
        k = 32
        r_winner = r_winner + k*(gain_winner-e_winner)
        r_loser = r_loser + k*(gain_loser-e_loser)
        self.tree.nodes[winner]['activity'] = r_winner
        self.tree.nodes[loser]['activity'] = r_loser

    def generate_distribution(self):
        """Generate a list, containing multiple uids of each structure"""
        distribution_list = list()
        for structure in list(self.tree.nodes):
            for i in range(self.tree.nodes[structure]['activity']):
                distribution_list.append(structure)
        return distribution_list

    def display_tree(self):
        self.tree_window.update_graph_network()


class SelectReferenceMode(Toplevel):
    def __init__(self, time_series):
        super().__init__()
        self.title("Select Reference Mode...")
        self.geometry("600x400+5+250")
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
    root.wm_title("Expansion Test")
    root.configure(background='#fff')
    ExpansionTest(root)
    root.mainloop()


if __name__ == '__main__':
    main()
