from tkinter import *
from tkinter import filedialog
from controller_bar import ControllerBar, ComparisonWindow, ReferenceModeWindow
from StockAndFlowInPython.session_handler import SessionHandler, SFDWindow, GraphNetworkWindow, NewGraphNetworkWindow
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from StockAndFlowInPython.similarity_calculation.similarity_calc import SimilarityCalculator
from StockAndFlowInPython.graph_sd.graph_based_engine import Structure, function_names, STOCK, FLOW, VARIABLE, \
    PARAMETER, CONNECTOR, ALIAS, \
    MULTIPLICATION, LINEAR
# from StockAndFlowInPython.structure_utilities import StructureUtilities
import pandas as pd
import numpy as np
import networkx as nx
import networkx.algorithms.isomorphism as iso
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
        self.concept_manager.generate_distribution()

        # Initialize builder rack
        self.possibility_rack = list()

        # Initialize structure manager
        self.structure_manager = StructureManager()
        root_structure = SessionHandler()
        root_structure.model_structure.add_stock(name='stock0', equation=50)
        self.structure_manager.add_structure(structure=root_structure)

        # Load reference mode
        self.load_reference_mode()

        # Display reference mode
        self.reference_modes_name_list = list(self.reference_modes.keys())
        self.reference_mode_window1 = ReferenceModeWindow(self.reference_modes[self.reference_modes_name_list[0]][1],
                                                          self.reference_modes_name_list[0])

        # Main loop
        random.seed(10)

        # Specify round to iterate
        self.iteration_time = 30
        i = 1
        while i <= self.iteration_time:
            print('Expansion: Iterating {}'.format(i))
            # self.structure_manager.derive_structure(self.structure_manager.uid - 1)
            self.generate_candidate_structure()
            # print(SimilarityCalculator.similarity_calc(np.array(self.reference_modes['stock0'][1]), np.array(self.concept_clds[0].model_structure.get_behavior('stock0'))))
            # for concept_cld in self.concept_manager.concept_clds:
            #     self.behavioral_similarity(who_compare=self.reference_modes['stock0'][1],
            #                                compare_with=self.concept_manager.concept_clds[concept_cld].model_structure.get_behavior('stock0'))
            self.structure_manager.cool_down()
            i += 1

    def generate_candidate_structure(self):
        """Generate a new candidate structure"""
        base = self.structure_manager.random_single()
        target = self.concept_manager.random_single()
        new = StructureUtilities.expand_structure(base_structure=base, target_structure=target)
        print('    Generated new candidate structure:', new)
        self.structure_manager.derive_structure(base_structure=base, new_structure=new)

    def behavioral_similarity(self, who_compare, compare_with):
        print("    Expansion: Calculating similarity...")

        distance, comparison_figure = SimilarityCalculator.similarity_calc(np.array(who_compare).reshape(-1, 1),
                                                                           np.array(compare_with).reshape(-1, 1))
        # ComparisonWindow(comparison_figure)
        return distance

    def adjust_concept_cld_likelihood(self, ):
        """As a result of a higher similarity to (part of) the reference mode"""
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
        select_dialog = SelectReferenceModeWindow(self.time_series)
        self.wait_window(select_dialog)  # important!
        reference_mode_type = select_dialog.reference_mode_type
        reference_mode_name = select_dialog.selected_reference_mode
        if reference_mode_type is not None and reference_mode_name is not None:
            self.reference_modes[reference_mode_name] = [reference_mode_type, self.time_series[reference_mode_name]]
            print("Added reference mode for {} : {}".format(reference_mode_type, reference_mode_name))

    def load_reference_mode(self):
        self.add_reference_mode()


class StructureUtilities(object):
    @staticmethod
    def calculate_structural_similarity(who_compare, compare_with):
        return

    @staticmethod
    def expand_structure(base_structure, target_structure):
        base = copy.deepcopy(base_structure)

        base_structure_stocks = base_structure.model_structure.all_stocks()
        start_with_stock_base = random.choice(base_structure_stocks)

        target_structure_stocks = target_structure.model_structure.all_stocks()
        start_with_stock_target = random.choice(target_structure_stocks)

        in_edges_in_target = target_structure.model_structure.sfd.in_edges(start_with_stock_base)

        # print("In_edges in target for {}".format(start_with_stock_base), in_edges_in_target)

        chosen_in_edge_in_target = random.choice(list(in_edges_in_target))
        # print("In_edge chosen: ", chosen_in_edge_in_target)

        subgraph_from_target = target_structure.model_structure.sfd.edge_subgraph([chosen_in_edge_in_target])

        base_structure.model_structure.sfd = nx.compose(base_structure.model_structure.sfd, subgraph_from_target)
        # print("New structure nodes:", base_structure.model_structure.sfd.nodes.data())
        # print("New structure edges:", base_structure.model_structure.sfd.edges.data())

        return base


class StructureManager(object):
    """The class containing and managing all variants of structures"""

    def __init__(self):
        self.tree = nx.DiGraph()
        self.uid = 0
        self.tree_window = NewGraphNetworkWindow(self.tree, "Expansion tree")
        self.candidate_structure_window = CandidateStructureWindow(self.tree)

    def generate_uid(self):
        """Get unique id for structure"""
        self.uid += 1
        return self.uid - 1

    def add_structure(self, structure):
        """Add a structure, usually as starting point"""
        self.tree.add_node(self.generate_uid(), structure=structure, activity=10)
        self.update_candidate_structure_window()

    def get_uid_by_structure(self, structure):
        for u in list(self.tree.nodes):
            if self.tree.nodes[u]['structure'] == structure:
                return u
        print(
            '    StructureManager: Can not find uid for given structure {}.'.format(structure.sfd.graph['structure_name']))

    def derive_structure(self, base_structure, new_structure):
        """Derive a new structure from an existing one"""
        # decide if this new_structure has been generated before. if so: add activity. if not: add it.
        # 1. identical to base_structure it self
        if nx.is_isomorphic(base_structure.model_structure.sfd, new_structure.model_structure.sfd):
            self.tree.nodes[self.get_uid_by_structure(base_structure)]['activity'] += 1
            print("The new structure is identical to the base structure")
            return
        for u in self.tree.neighbors(self.get_uid_by_structure(base_structure)):
            if nx.is_isomorphic(self.tree.nodes[u]['structure'].model_structure.sfd, new_structure.model_structure.sfd):
                self.tree.nodes[u]['activity'] += 1
                print("The new structure already exists in base structure's neighbours")
                return

        # add a new node
        new_uid = self.generate_uid()
        print('    Deriving structure from {} to {}'.format(base_structure, new_structure))
        self.tree.add_node(new_uid,
                           structure=new_structure,
                           activity=self.tree.nodes[self.get_uid_by_structure(base_structure)]['activity']
                           )
        # build a link from the old to the new
        self.tree.add_edge(self.get_uid_by_structure(base_structure), new_uid)
        self.update_candidate_structure_window()

    def cool_down(self):
        """Update structures' activity (cooling down) after one iteration"""
        for u in self.tree.nodes:
            self.tree.nodes[u]['activity'] = self.tree.nodes[u]['activity'] - 1

    def random_single(self):
        """Return one structure"""
        random_structure_uid = random.choice(self.generate_distribution())
        print('    Random structure found:', self.tree.nodes[random_structure_uid])
        return self.tree.nodes[random_structure_uid]['structure']

    def random_pair(self):
        """Return a pair of structures for competition"""
        random_structures_uid = random.choices(self.generate_distribution(), k=2)
        return self.tree.nodes[random_structures_uid[0]]['structure'], \
               self.tree.nodes[random_structures_uid[1]]['structure']

    def update_activity_elo(self, winner, loser):
        """Update winner and loser's activity using Elo Rating System"""
        r_winner = self.tree.nodes[winner]['activity']
        r_loser = self.tree.nodes[loser]['activity']
        e_winner = 1 / (1 + 10 ** ((r_loser - r_winner) / 400))
        e_loser = 1 / (1 + 10 ** ((r_winner - r_loser) / 400))
        gain_winner = 1
        gain_loser = 0
        k = 32
        r_winner = r_winner + k * (gain_winner - e_winner)
        r_loser = r_loser + k * (gain_loser - e_loser)
        self.tree.nodes[winner]['activity'] = r_winner
        self.tree.nodes[loser]['activity'] = r_loser

    def generate_distribution(self):
        """Generate a list, containing multiple uids of each structure"""
        distribution_list = list()
        for u in list(self.tree.nodes):
            for i in range(self.tree.nodes[u]['activity']):
                distribution_list.append(u)
        return distribution_list

    def display_tree(self):
        self.tree_window.update_graph_network()

    def update_candidate_structure_window(self):
        try:
            self.candidate_structure_window.candidate_structure_list.destroy()
        except:
            pass
        self.display_tree()
        self.candidate_structure_window.generate_candidate_structure_list()


class ConceptManager(object):
    """The class containing and managing all concept clds"""

    def __init__(self):
        self.concept_clds = dict()

        self.add_concept_cld(name='basic_stock_inflow')
        self.add_concept_cld(name='basic_stock_outflow')
        self.add_concept_cld(name='first_order_positive')
        self.add_concept_cld(name='first_order_negative')

    def add_concept_cld(self, name, likelihood=10):
        a = SessionHandler()
        a.model_structure.set_predefined_structure[name]()
        a.model_structure.simulate(simulation_time=25)
        a.model_structure.sfd.graph['likelihood'] = likelihood
        self.concept_clds[name] = a

    def get_concept_cld_by_name(self, name):
        for concept_cld in self.concept_clds:
            if concept_cld.model_structure.sfd.graph['structure_name'] == name:
                return concept_cld

    def generate_distribution(self):
        """Generate a list, containing multiple uids of each structure"""
        distribution_list = list()
        for concept_cld in self.concept_clds.keys():
            for i in range(self.concept_clds[concept_cld].model_structure.sfd.graph['likelihood']):
                distribution_list.append(self.concept_clds[concept_cld].model_structure.sfd.graph['structure_name'])
        # print('Concept CLD distribution list:', distribution_list)
        return distribution_list

    def random_single(self):
        """Return one structure"""
        random_concept_cld_name = random.choice(self.generate_distribution())
        print('    Random concept CLD found:', random_concept_cld_name)
        return self.concept_clds[random_concept_cld_name]

    def random_pair(self):
        """Return a pair of structures for competition"""
        return random.choices(self.generate_distribution(), k=2)

    def update_likelihood_elo(self, winner, loser):
        """Update winner and loser's activity using Elo Rating System"""
        r_winner = self.get_concept_cld_by_name(winner).model_structure.sfd.graph['likelihood']
        r_loser = self.get_concept_cld_by_name(loser).model_structure.sfd.graph['likelihood']
        e_winner = 1 / (1 + 10 ** ((r_loser - r_winner) / 400))
        e_loser = 1 / (1 + 10 ** ((r_winner - r_loser) / 400))
        gain_winner = 1
        gain_loser = 0
        k = 32
        r_winner = r_winner + k * (gain_winner - e_winner)
        r_loser = r_loser + k * (gain_loser - e_loser)
        self.get_concept_cld_by_name(winner).model_structure.sfd.graph['likelihood'] = r_winner
        self.get_concept_cld_by_name(loser).model_structure.sfd.graph['likelihood'] = r_loser


class CandidateStructureWindow(Toplevel):
    def __init__(self, tree):
        super().__init__()
        self.title("Display Candidate Structure")
        self.geometry("600x400+5+750")

        self.selected_candidate_structure = None
        self.fm_select = Frame(self)
        self.fm_select.pack(side=LEFT)

        self.tree = tree

        self.fm_display = Frame(self)
        self.fm_display.pack(side=LEFT)

        self.generate_candidate_structure_list()

    def generate_candidate_structure_list(self):
        self.candidate_structure_list = Listbox(self.fm_select)
        self.candidate_structure_list.pack(side=TOP)
        for u in list(self.tree.nodes):
            # print("adding entry", u)
            self.candidate_structure_list.insert(END, u)
        self.candidate_structure_list.bind('<<ListboxSelect>>', self.display_candidate_structure)

    def display_candidate_structure(self, evt):
        selected_entry = self.candidate_structure_list.get(self.candidate_structure_list.curselection())
        self.selected_candidate_structure = self.tree.nodes[selected_entry]['structure']
        try:
            plt.close()
            self.candidate_structure_canvas.get_tk_widget().destroy()
        except:
            pass
        fig, ax = plt.subplots()

        node_attrs_function = nx.get_node_attributes(self.selected_candidate_structure.model_structure.sfd, 'function')
        custom_node_attrs = dict()
        for node, attr in node_attrs_function.items():
            custom_node_attrs[node] = "{}={}".format(node, attr)

        nx.draw(self.selected_candidate_structure.model_structure.sfd,
                labels= custom_node_attrs
                #with_labels=True
                )
        self.candidate_structure_canvas = FigureCanvasTkAgg(figure=fig, master=self.fm_display)
        self.candidate_structure_canvas.get_tk_widget().pack(side=LEFT)
        self.update()


class SelectReferenceModeWindow(Toplevel):
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
        self.radio_button_type_3 = Radiobutton(self.fm_select, text='Auxiliary', variable=self.ref_md_type,
                                               value=VARIABLE)
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
        self.reference_mode_plot.plot(self.time_series[self.time_series_list.get(self.time_series_list.curselection())],
                                      '*')
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
    root.geometry("+5+50")
    root.wm_title("Expansion Test")
    root.configure(background='#fff')
    ExpansionTest(root)
    root.mainloop()


if __name__ == '__main__':
    main()
