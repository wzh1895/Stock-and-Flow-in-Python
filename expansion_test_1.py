from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config import ITERATION_TIME, ACTIVITY_DEMOMINATOR, INITIAL_LIKELIHOOD, INITIAL_ACTIVITY, REFERENCE_MODE_PATH, \
    COOL_DOWN_TIMES, COOL_DOWN_SWITCH
from StockAndFlowInPython.session_handler import SessionHandler, SFDWindow, GraphNetworkWindow, NewGraphNetworkWindow
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
import time


class ExpansionTest(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(width=200)
        self.pack(fill=BOTH, expand=1)

        self.session_handler1 = SessionHandler()

        self.menubar = Menu(self.master)
        self.file_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='File', menu=self.file_menu)

        self.action_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='Action', menu=self.action_menu)
        self.action_menu.add_command(label='Main loop', command=self.main_loop)

        self.reference_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='Reference', menu=self.reference_menu)
        self.reference_menu.add_command(label='Add reference mode', command=self.add_reference_mode)

        self.master.config(menu=self.menubar)

        self.fm_controller1 = Frame(self.master)
        self.fm_controller1.pack(side=TOP)
        self.variables_in_model = ["Variable"]

        self.fm_controller2 = Frame(self.master)
        self.fm_controller2.pack(side=TOP)

        self.fm_suggestion = Frame(self.master)
        self.fm_suggestion.pack(side=TOP)

        # Initialize concept CLDs (generic structures)
        self.concept_manager = ConceptManager()
        self.concept_manager.generate_distribution()

        # Initialize builder rack
        self.possibility_rack = list()

        # Initialize structure manager
        self.structure_manager = StructureManager()
        root_structure = SessionHandler()
        root_structure.build_stock(name='stock0', initial_value=50, x=100, y=100)
        root_structure.simulation_handler(25)
        self.structure_manager.add_structure(structure=root_structure)
        self.structure_manager.if_can_simulate[0] = True

        # Reference modes
        self.reference_modes = dict()

        # Initialize reference mode manager
        self.reference_mode_manager = ReferenceModeManager(self.reference_modes)

        # self.reference_mode_manager.add_reference_mode()

        # Main loop
        # self.main_loop()

    def main_loop(self):
        # Specify round to iterate
        self.iteration_time = ITERATION_TIME
        i = 1
        while i <= self.iteration_time:
            print('\n\nExpansion: Iterating {}'.format(i))

            # STEP1 adjust concept CLDs' likelihood
            for j in range(3):
                self.update_concept_clds_likelihood()

            # STEP2 generate new candidate structure
            self.generate_candidate_structure()

            # STEP3 adjust candidate structures' activity
            self.update_candidate_structure_activity()

            # STEP3 cool down those not simulatable structures
            if COOL_DOWN_SWITCH:
                for k in range(COOL_DOWN_TIMES):
                    self.structure_manager.cool_down()
            i += 1

    def add_reference_mode(self):
        self.reference_mode_manager.add_reference_mode()

    def update_candidate_structure_activity(self):
        if len(self.structure_manager.tree.nodes) > 5:  # only do this when there are more than 3 candidates
            # TODO: improve this control, not using ballpark number
            # Get 2 random candidates
            random_two_candidates = [None, None]
            while random_two_candidates[0] == random_two_candidates[1]:
                random_two_candidates = self.structure_manager.random_pair()
                while not (self.structure_manager.if_can_simulate[random_two_candidates[0]] and self.structure_manager.if_can_simulate[random_two_candidates[1]]):
                    # we have to get two simulatable structures to compare their behaviors
                    random_two_candidates = self.structure_manager.random_pair()
            print("Two candidate structures chosen for comparison: ", random_two_candidates)
            # Calculate their similarity to reference mode
            random_two_candidates_distance = {random_two_candidates[0]: self.behavioral_distance(
             self.structure_manager.tree.nodes[random_two_candidates[0]]['structure'].model_structure.sfd.node['stock0']['value'],
             self.reference_modes['stock0'][1]
            ),
                                                random_two_candidates[1]: self.behavioral_distance(
             self.structure_manager.tree.nodes[random_two_candidates[1]]['structure'].model_structure.sfd.node['stock0']['value'],
             self.reference_modes['stock0'][1]
            )
            }
            print(random_two_candidates_distance)
            # Update their activity
            if random_two_candidates_distance[random_two_candidates[0]] != random_two_candidates_distance[random_two_candidates[1]]:
                if random_two_candidates_distance[random_two_candidates[0]] > random_two_candidates_distance[random_two_candidates[1]]:
                    self.structure_manager.update_activity_elo(random_two_candidates[1], random_two_candidates[0])
                else:
                    self.structure_manager.update_activity_elo(random_two_candidates[0], random_two_candidates[1])
            print(self.structure_manager.show_all_activity())

    def update_concept_clds_likelihood(self):
        random_two_clds = [None, None]
        while random_two_clds[0] == random_two_clds[1]:  # The two cannot be the same
            random_two_clds = self.concept_manager.random_pair()
        # print(random_two_clds)
        random_two_clds_distance = {random_two_clds[0]: self.behavioral_distance(
            self.concept_manager.concept_clds[random_two_clds[0]].model_structure.sfd.node['stock0']['value'],
            self.reference_modes['stock0'][1]),
            random_two_clds[1]: self.behavioral_distance(
                self.concept_manager.concept_clds[random_two_clds[1]].model_structure.sfd.node['stock0']['value'],
                self.reference_modes['stock0'][1])
        }
        # print(random_two_clds_distance)
        # a larger distance -> a lower likelihood
        if random_two_clds_distance[random_two_clds[0]] < random_two_clds_distance[random_two_clds[1]]:
            self.concept_manager.update_likelihood_elo(random_two_clds[0], random_two_clds[1])
        else:
            self.concept_manager.update_likelihood_elo(random_two_clds[1], random_two_clds[0])
        print(self.concept_manager.concept_clds_likelihood)


    def generate_candidate_structure(self):
        """Generate a new candidate structure"""
        base = self.structure_manager.random_single()
        target = self.concept_manager.random_single()
        new = StructureUtilities.expand_structure(base_structure=base, target_structure=target)
        # print('    Generated new candidate structure:', new)
        self.structure_manager.derive_structure(base_structure=base, new_structure=new)

    def behavioral_distance(self, who_compare, compare_with):
        print("    Expansion: Calculating similarity...")
        distance, comparison_figure = SimilarityCalculator.similarity_calc(np.array(who_compare).reshape(-1, 1),
                                                                           np.array(compare_with).reshape(-1, 1))
        # ComparisonWindow(comparison_figure)
        return distance

    def adjust_concept_cld_likelihood(self, ):
        """As a result of a higher similarity to (part of) the reference mode"""
        pass


class ReferenceModeManager(Toplevel):
    def __init__(self, reference_modes, reference_mode_path=REFERENCE_MODE_PATH, width=600, height=400, x=5, y=130):
        super().__init__()
        self.title("Reference Mode Manager")
        self.geometry("{}x{}+{}+{}".format(width, height, x, y))

        self.reference_mode_path = reference_mode_path
        self.numerical_data = None
        self.time_series = dict()
        self.reference_modes = reference_modes

        self.fm_select = Frame(self)
        self.fm_select.pack(side=LEFT)
        self.lb_select = Label(self.fm_select, text='Reference\nModes', font=7)
        self.lb_select.pack(anchor='nw')

        self.fm_display = Frame(self)
        self.fm_display.pack(side=LEFT)

        self.generate_reference_mode_list_box()

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
        self.generate_reference_mode_list_box()

    def generate_reference_mode_list_box(self):
        try:
            self.reference_mode_list_box.destroy()
        except AttributeError:
            pass
        self.reference_mode_list_box = Listbox(self.fm_select)
        self.reference_mode_list_box.pack(side=TOP)

        for ref_mode in self.reference_modes.keys():
            self.reference_mode_list_box.insert(END, ref_mode)
        self.reference_mode_list_box.bind('<<ListboxSelect>>', self.show_reference_mode)

    def show_reference_mode(self, evt):
        try:
            self.reference_mode_graph.get_tk_widget().destroy()
        except AttributeError:
            pass
        self.reference_mode_figure = Figure(figsize=(5, 4))
        self.reference_mode_plot = self.reference_mode_figure.add_subplot(111)
        self.reference_mode_plot.plot(self.time_series[self.reference_mode_list_box.get(self.reference_mode_list_box.curselection())], '*')
        self.reference_mode_plot.set_xlabel("Time")
        self.reference_mode_plot.set_ylabel(self.reference_mode_list_box.get(self.reference_mode_list_box.curselection()))
        self.reference_mode_graph = FigureCanvasTkAgg(self.reference_mode_figure, master=self.fm_display)
        self.reference_mode_graph.draw()
        self.reference_mode_graph.get_tk_widget().pack(side=LEFT)


class StructureUtilities(object):
    @staticmethod
    def calculate_structural_similarity(who_compare, compare_with):
        return

    @staticmethod
    def expand_structure(base_structure, target_structure):
        new_base = copy.deepcopy(base_structure)
        print("    Base_structure: ", new_base.model_structure.sfd.nodes(data='function', default='Not available'))

        # Base

        # get all elements in base structure
        base_structure_elements = list(new_base.model_structure.sfd.nodes)
        # pick an element from base_structure to start with. Now: randomly. Future: guided by activity.
        start_with_element_base = random.choice(base_structure_elements)
        # print("    {} in base_structure is chosen to start with".format(start_with_element_base))
        # print("    Details: ", new_base.model_structure.sfd.nodes[start_with_element_base]['function'])

        # get all in_edges into this element in base_structure
        in_edges_in_base = new_base.model_structure.sfd.in_edges(start_with_element_base)
        # print("    In_edges in base_structure for {}".format(start_with_element_base),
        #       [in_edge_in_base[0] for in_edge_in_base in in_edges_in_base])

        # Target

        # get all elements in target structure
        target_structure_elements = list(target_structure.model_structure.sfd.nodes)

        # pick an element from target_structure to start with. Now: randomly. Future: guided by activity.
        start_with_element_target = random.choice(target_structure_elements)
        # print("    {} in target_structure is chosen to start with".format(start_with_element_target))
        # print("    Details: ", target_structure.model_structure.sfd.nodes[start_with_element_target])

        # get all in_edges into this element in target_structure
        in_edges_in_target = target_structure.model_structure.sfd.in_edges(start_with_element_target)
        # make sure the element to start with is not an end (boundary)
        while len(in_edges_in_target) == 0:
            start_with_element_target = random.choice(target_structure_elements)
            in_edges_in_target = target_structure.model_structure.sfd.in_edges(start_with_element_target)
        # print("    In_edges in target_structure for {}".format(start_with_element_target),
        #       [in_edge_in_target[0] for in_edge_in_target in in_edges_in_target])

        # pick an in_edge from all in_edges into this element in target_structure
        chosen_in_edge_in_target = random.choice(list(in_edges_in_target))
        # print("    In_edge chosen in target_structure: ", chosen_in_edge_in_target[0], '--->',
        #       chosen_in_edge_in_target[1])

        # Merge

        # extract the part of structure containing this in_edge in target_structure
        subgraph_from_target = target_structure.model_structure.sfd.edge_subgraph([chosen_in_edge_in_target])
        # print("    Subgraph from target_structure:{} ".format(subgraph_from_target.nodes(data='function')))

        new_base.model_structure.sfd = nx.compose(new_base.model_structure.sfd, subgraph_from_target)

        # check and fix dependencies
        # print(chosen_in_edge_in_target[1])
        in_edges_to_new_node = target_structure.model_structure.sfd.in_edges(chosen_in_edge_in_target[1])
        # print(in_edges_to_new_node)
        for in_edge in in_edges_to_new_node:
            if in_edge[0] in new_base.model_structure.sfd.nodes and in_edge not in new_base.model_structure.sfd.edges:
                print("Found a missing edge: ", in_edge)
                new_base.model_structure.sfd.add_edge(*in_edge)

        # print("New structure nodes:", new_base.model_structure.sfd.nodes.data('function'))
        # print("New structure edges:", new_base.model_structure.sfd.edges.data())

        return new_base


class StructureManager(object):
    """The class containing and managing all variants of structures"""

    def __init__(self):
        self.tree = nx.DiGraph()
        self.uid = 0
        self.tree_window = NewGraphNetworkWindow(self.tree, window_title="Expansion tree", node_color="skyblue", width=800, height=800, x=800, y=50, attr='activity')
        self.candidate_structure_window = CandidateStructureWindow(self.tree)
        self.if_can_simulate = dict()

    def show_all_activity(self):
        all_activity = nx.get_node_attributes(self.tree, 'activity')
        return all_activity

    def generate_uid(self):
        """Get unique id for structure"""
        self.uid += 1
        return self.uid - 1

    def add_structure(self, structure):
        """Add a structure, usually as starting point"""
        self.tree.add_node(self.generate_uid(), structure=structure, activity=INITIAL_ACTIVITY)
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
        # if nx.is_isomorphic(base_structure.model_structure.sfd, new_structure.model_structure.sfd):
        GM = iso.DiGraphMatcher(base_structure.model_structure.sfd, new_structure.model_structure.sfd,
                                node_match=iso.categorical_node_match(attr=['function'], default=[None])
                                # node_match=iso.categorical_node_match(attr=['equation', 'value'], default=[None, None])
                                )
        if GM.is_isomorphic():
            self.tree.nodes[self.get_uid_by_structure(base_structure)]['activity'] += 1
            print("    The new structure is identical to the base structure")
            return
        # 2. identical to a neighbor of the base_structure
        for neighbour in self.tree.neighbors(self.get_uid_by_structure(base_structure)):
            GM = iso.DiGraphMatcher(self.tree.nodes[neighbour]['structure'].model_structure.sfd,
                                    new_structure.model_structure.sfd,
                                    node_match=iso.categorical_node_match(attr=['function'], default=[None])
                                    # node_match=iso.categorical_node_match(attr=['equation', 'value'], default=[None, None])
                                    )
            if GM.is_isomorphic():
            # if nx.is_isomorphic(self.tree.nodes[neighbour]['structure'].model_structure.sfd, new_structure.model_structure.sfd):
                self.tree.nodes[neighbour]['activity'] += 1
                # print(self.tree.nodes[neighbour]['structure'].model_structure.sfd.nodes(data=True))
                # print(new_structure.model_structure.sfd.nodes(data=True))
                print("    The new structure already exists in base structure's neighbours")
                return

        # add a new node
        new_uid = self.generate_uid()
        print('    Deriving structure from {} to {}'.format(self.get_uid_by_structure(base_structure), new_uid))
        new_activity = self.tree.nodes[self.get_uid_by_structure(base_structure)]['activity']//ACTIVITY_DEMOMINATOR
        self.tree.add_node(new_uid,
                           structure=new_structure,
                           activity=new_activity
                           )

        # subtract this part of activity from the base_structure
        self.tree.nodes[self.get_uid_by_structure(base_structure)]['activity'] -= new_activity
        if self.tree.nodes[self.get_uid_by_structure(base_structure)]['activity'] < 1:
            self.tree.nodes[self.get_uid_by_structure(base_structure)]['activity'] = 1

        # build a link from the old structure to the new structure
        self.tree.add_edge(self.get_uid_by_structure(base_structure), new_uid)
        # simulate this new structure
        try:
            new_structure.simulation_handler(25)
            self.if_can_simulate[new_uid] = True
        except KeyError:
            self.if_can_simulate[new_uid] = False

        print("Simulatable structures:", self.if_can_simulate)

        self.update_candidate_structure_window()

    def cool_down(self):
        """Cool down those not simulatable structures"""
        # for u in self.tree.nodes:
        for u in [structure for structure in self.if_can_simulate.keys() if self.if_can_simulate[structure] is False]:
            self.tree.nodes[u]['activity'] = self.tree.nodes[u]['activity'] - 1 if self.tree.nodes[u]['activity'] > 1 else 1
        self.update_candidate_structure_window()

    def random_single(self):
        """Return one structure"""
        random_structure_uid = random.choice(self.generate_distribution())
        print('    No. {} is chosen as base_structure;'.format(random_structure_uid))
        return self.tree.nodes[random_structure_uid]['structure']

    def random_pair(self):
        """Return a pair of structures for competition"""
        random_structures_uid = random.choices(self.generate_distribution(), k=2)
        # return self.tree.nodes[random_structures_uid[0]]['structure'], \
        #        self.tree.nodes[random_structures_uid[1]]['structure']
        return random_structures_uid

    def update_activity_elo(self, winner, loser):
        """Update winner and loser's activity using Elo Rating System"""
        r_winner = self.tree.nodes[winner]['activity']
        r_loser = self.tree.nodes[loser]['activity']
        e_winner = 1 / (1 + 10 ** ((r_loser - r_winner) / 400))
        e_loser = 1 / (1 + 10 ** ((r_winner - r_loser) / 400))
        gain_winner = 1
        gain_loser = 0
        # maximum activity one can get or lose in a round of comparison
        k = 4
        r_winner = r_winner + k * (gain_winner - e_winner)
        r_loser = r_loser + k * (gain_loser - e_loser)
        self.tree.nodes[winner]['activity'] = round(r_winner) if r_winner > 0 else 1
        self.tree.nodes[loser]['activity'] = round(r_loser) if r_loser > 0 else 1

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
        # try:
        #     self.candidate_structure_window.candidate_structure_list_box.destroy()
        # except:
        #     pass
        self.display_tree()
        self.candidate_structure_window.generate_candidate_structure_list()


class ConceptManager(object):
    """The class containing and managing all concept CLDs"""

    def __init__(self):
        self.concept_clds = dict()
        self.concept_clds_likelihood = dict()
        self.add_concept_cld(name='basic_stock_inflow')
        self.add_concept_cld(name='basic_stock_outflow')
        self.add_concept_cld(name='first_order_positive')
        self.add_concept_cld(name='first_order_negative')

        self.concept_clds_likelihood_window = ConceptCLDsLikelihoodWindow(concept_clds_likelihood=self.concept_clds_likelihood)
        self.concept_clds_likelihood_window.create_likelihood_display()


    def add_concept_cld(self, name, likelihood=INITIAL_LIKELIHOOD):
        a = SessionHandler()
        a.model_structure.set_predefined_structure[name]()
        a.model_structure.simulate(simulation_time=25)
        # a.model_structure.sfd.graph['likelihood'] = likelihood
        self.concept_clds[name] = a
        self.concept_clds_likelihood[name] = likelihood

    # def get_concept_cld_by_name(self, name):
    #     for concept_cld in self.concept_clds:
    #         if concept_cld.model_structure.sfd.graph['structure_name'] == name:
    #             return concept_cld

    def generate_distribution(self):
        """Generate a list, containing multiple uids of each structure"""
        distribution_list = list()
        # for concept_cld in self.concept_clds.keys():
        #     for i in range(self.concept_clds[concept_cld].model_structure.sfd.graph['likelihood']):
        #         distribution_list.append(self.concept_clds[concept_cld].model_structure.sfd.graph['structure_name'])
        # print('Concept CLD distribution list:', distribution_list)
        for concept_cld in self.concept_clds_likelihood.keys():
            for i in range(self.concept_clds_likelihood[concept_cld]):
                distribution_list.append(concept_cld)
        return distribution_list

    def random_single(self):
        """Return one structure"""
        random_concept_cld_name = random.choice(self.generate_distribution())
        print('    {} is chosen as target_structure;'.format(random_concept_cld_name))
        return self.concept_clds[random_concept_cld_name]

    def random_pair(self):
        """Return a pair of structures for competition"""
        random_two = random.choices(self.generate_distribution(), k=2)
        # return self.concept_clds[random_two[0]], self.concept_clds[random_two[1]]
        return random_two

    def update_likelihood_elo(self, winner, loser):
        """Update winner and loser's activity using Elo Rating System"""
        # r_winner = self.concept_clds[winner].model_structure.sfd.graph['likelihood']
        # r_loser = self.concept_clds[loser].model_structure.sfd.graph['likelihood']
        r_winner = self.concept_clds_likelihood[winner]
        r_loser = self.concept_clds_likelihood[loser]
        e_winner = 1 / (1 + 10 ** ((r_loser - r_winner) / 400))
        e_loser = 1 / (1 + 10 ** ((r_winner - r_loser) / 400))
        gain_winner = 1
        gain_loser = 0
        k = 16
        r_winner = r_winner + k * (gain_winner - e_winner)
        r_loser = r_loser + k * (gain_loser - e_loser)
        # self.concept_clds[winner].model_structure.sfd.graph['likelihood'] = r_winner
        # self.concept_clds[loser].model_structure.sfd.graph['likelihood'] = r_loser
        self.concept_clds_likelihood[winner] = round(r_winner) if r_winner > 0 else 1
        self.concept_clds_likelihood[loser] = round(r_loser) if r_loser > 0 else 1

        self.concept_clds_likelihood_window.update_likelihood_display()


class CandidateStructureWindow(Toplevel):
    def __init__(self, tree, width=1200, height=400, x=5, y=700):
        super().__init__()
        self.title("Display Candidate Structure")
        self.geometry("{}x{}+{}+{}".format(width, height, x, y))

        self.selected_candidate_structure = None
        self.fm_select = Frame(self)
        self.fm_select.pack(side=LEFT)

        self.lb_select = Label(self.fm_select, text='Candidate\nSturctures', font=7)
        self.lb_select.pack(anchor='nw')

        self.tree = tree

        self.fm_display_structure = Frame(self)
        self.fm_display_structure.configure(width=500)
        self.fm_display_structure.pack(side=LEFT)

        self.fm_display_behaviour = Frame(self)
        self.fm_display_behaviour.configure(width=500)
        self.fm_display_behaviour.pack(side=LEFT)
        self.generate_candidate_structure_list()

    def generate_candidate_structure_list(self):
        try:
            self.candidate_structure_list_box.destroy()
            self.candidate_structure_list_scrollbar.destroy()
        except AttributeError:
            pass

        self.candidate_structure_list_box = Listbox(self.fm_select)
        self.candidate_structure_list_box.configure(width=10, height=20)
        self.candidate_structure_list_box.pack(side=LEFT, fill=Y)

        self.candidate_structure_list_scrollbar = Scrollbar(self.fm_select, orient="vertical")
        self.candidate_structure_list_scrollbar.config(command=self.candidate_structure_list_box.yview)
        self.candidate_structure_list_scrollbar.pack(side=RIGHT, fill=Y)

        for u in list(self.tree.nodes):
            # print("adding entry", u)
            self.candidate_structure_list_box.insert(END, u)
        self.candidate_structure_list_box.bind('<<ListboxSelect>>', self.display_candidate)

    def display_candidate(self, evt):
        self.display_candidate_structure()
        self.display_candidate_behaviour()

    def display_candidate_structure(self):
        selected_entry = self.candidate_structure_list_box.get(self.candidate_structure_list_box.curselection())
        self.selected_candidate_structure = self.tree.nodes[selected_entry]['structure']

        try:
            plt.close()
            self.candidate_structure_canvas.get_tk_widget().destroy()
        except:
            pass
        fig, ax = plt.subplots()

        node_attrs_function = nx.get_node_attributes(self.selected_candidate_structure.model_structure.sfd, 'function')
        node_attrs_value = nx.get_node_attributes(self.selected_candidate_structure.model_structure.sfd, 'value')
        custom_node_attrs = dict()
        for node, attr in node_attrs_function.items():
            # when the element only has a value but no function
            if attr is None:
                attr = node_attrs_value[node][0]
            # when the element has a function
            else:
                attr = [attr[0]] + [factor[0] for factor in attr[1:]]
            custom_node_attrs[node] = "{}={}".format(node, attr)

        nx.draw(self.selected_candidate_structure.model_structure.sfd,
                labels=custom_node_attrs,
                font_size=6
                #with_labels=True
                )
        self.candidate_structure_canvas = FigureCanvasTkAgg(figure=fig, master=self.fm_display_structure)
        self.candidate_structure_canvas.get_tk_widget().pack(side=LEFT)

        # Display behavior
        self.update()

    def display_candidate_behaviour(self):
        try:
            self.simulation_result_canvas.get_tk_widget().destroy()
        except:
            pass

        selected_entry = self.candidate_structure_list_box.get(self.candidate_structure_list_box.curselection())
        self.selected_candidate_structure = self.tree.nodes[selected_entry]['structure']

        # self.selected_candidate_structure.simulation_handler(25)

        result_figure = self.selected_candidate_structure.model_structure.draw_results(names=['stock0'], rtn=True)
        self.simulation_result_canvas = FigureCanvasTkAgg(figure=result_figure, master=self.fm_display_behaviour)
        self.simulation_result_canvas.get_tk_widget().pack(side=LEFT)

        # Display result
        self.update()


class SelectReferenceModeWindow(Toplevel):
    def __init__(self, time_series, width=600, height=400, x=5, y=130):
        super().__init__()
        self.title("Select Reference Mode...")
        self.geometry("{}x{}+{}+{}".format(width, height, x, y))
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


class ConceptCLDsLikelihoodWindow(Toplevel):
    def __init__(self, concept_clds_likelihood=None, window_title="Concept CLDs", width=200, height=150, x=5, y=200):
        super().__init__()
        self.title(window_title)
        self.width = width
        self.height = height
        self.geometry("{}x{}+{}+{}".format(width, height, x, y))
        self.concept_clds_likelihood = concept_clds_likelihood

        self.fm_labels = Frame(master=self, width=self.width)
        self.fm_labels.pack(side=LEFT, anchor='nw')

        self.labels = list()

    def create_likelihood_display(self):
        for item, llikelihood in self.concept_clds_likelihood.items():
            text = item + " : " + str(llikelihood)
            self.labels.append(Label(self.fm_labels, text=text, font=6))
            self.labels[-1].pack(side=TOP, anchor='w')

    def update_likelihood_display(self):
        try:
            self.fm_labels.destroy()
        except:
            pass
        self.fm_labels = Frame(master=self, width=self.width)
        self.fm_labels.pack(side=LEFT, anchor='nw')
        self.create_likelihood_display()


def main():
    root = Tk()
    root.geometry("+5+50")
    root.wm_title("Expansion Test")
    root.configure(background='#fff')
    ExpansionTest(root)
    root.mainloop()


if __name__ == '__main__':
    main()
