from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config import ITERATION_TIME, ACTIVITY_DEMOMINATOR
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


class ExpansionTest(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill=BOTH, expand=1)

        self.session_handler1 = SessionHandler()

        self.menubar = Menu(self.master)
        self.filemenu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='File', menu=self.filemenu)
        self.filemenu.add_command(label='Load reference', command=self.load_reference_mode)

        self.master.config(menu=self.menubar)

        # self.lb_name = Label(self.master, text='System Dynamics Model', background="#fff")
        # self.lb_name.pack(side=TOP)
        self.fm_controller1 = Frame(self.master)
        self.fm_controller1.pack(side=TOP)
        # self.btn_load_model = Button(self.fm_controller1, text="Load model", command=self.load_model)
        # self.btn_load_model.pack(side=LEFT)
        # self.btn_run = Button(self.fm_controller1, text="Simulate", command=self.simulate)
        # self.btn_run.pack(side=LEFT)
        # self.variables_list = ttk.Combobox(self.fm_controller1)
        self.variables_in_model = ["Variable"]
        # self.variables_list["values"] = self.variables_in_model
        # self.variables_list.current(0)
        # self.variables_list.bind("<<ComboboxSelected>>", self.select_variable)
        # self.variables_list.pack(side=LEFT)
        # self.sim_time = StringVar()
        # self.sim_time.set("20")
        # self.entry1 = Entry(self.fm_controller1, width=10, textvariable=self.sim_time)
        # self.entry1.pack()

        self.fm_controller2 = Frame(self.master)
        self.fm_controller2.pack(side=TOP)
        # self.btn_show_result = Button(self.fm_controller2, text="Show result",
        #                               command=self.session_handler1.show_result)
        # self.btn_show_result.pack(side=LEFT)
        # self.btn_reset = Button(self.fm_controller2, text="Reset", command=self.session_handler1.reset)
        # self.btn_reset.pack(side=LEFT)
        # self.btn_clear_run = Button(self.fm_controller2, text="Clear a run", command=self.session_handler1.clear_a_run)
        # self.btn_clear_run.pack(side=LEFT)
        # self.btn_refresh = Button(self.fm_controller2, text="Refresh", command=self.session_handler1.refresh)
        # self.btn_refresh.pack(side=LEFT)

        # Suggestion

        self.reference_mode_path = './StockAndFlowInPython/case/tea_cup_model.csv'
        # self.reference_mode_path = './StockAndFlowInPython/case/bank_account_model.csv'
        # self.similarity_calculator1 = SimilarityCalculator()

        self.fm_suggestion = Frame(self.master)
        self.fm_suggestion.pack(side=TOP)
        self.btn_load_reference_mode = Button(self.fm_suggestion, text="Load reference Mode", command=self.load_reference_mode)
        self.btn_load_reference_mode.pack(side=LEFT)
        # self.btn_calculate_similarity = Button(self.fm_suggestion, text="Calculate similarity", command=self.calculate_similarity)
        # self.btn_calculate_similarity.pack(side=LEFT)
        # self.btn_load_generic_structure = Button(self.fm_suggestion, text="Load closest structure", command=self.load_generic_structure)
        # self.btn_load_generic_structure.pack(side=LEFT)
        # self.lb_suggested_generic_stucture = Label(self.master, text="Reference mode pattern", background='#fff')
        # self.lb_suggested_generic_stucture.pack(side=TOP)
        # Overwriting
        # self.btn_load_reference_mode = Button(self.fm_suggestion, text="Load reference Mode", command=self.load_reference_mode)

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
        root_structure.build_stock(name='stock0', initial_value=50, x=100, y=100)
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
        self.iteration_time = ITERATION_TIME
        i = 1
        while i <= self.iteration_time:
            print('Expansion: Iterating {}'.format(i))
            self.generate_candidate_structure()
            # print(SimilarityCalculator.similarity_calc(np.array(self.reference_modes['stock0'][1]), np.array(self.concept_clds[0].model_structure.get_behavior('stock0'))))
            # for concept_cld in self.concept_manager.concept_clds:
            #     self.behavioral_similarity(who_compare=self.reference_modes['stock0'][1],
            #                                compare_with=self.concept_manager.concept_clds[concept_cld].model_structure.get_behavior('stock0'))
            # self.structure_manager.cool_down()
            i += 1

    def simulate(self):
        self.session_handler1.simulation_handler(simulation_time=int(self.entry1.get()))
        self.variables_list['values'] = self.session_handler1.variables_in_model

    def load_model(self):
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

    def calculate_similarity(self):
        self.suggested_generic_structure, self.comparison_figure = SimilarityCalculator.categorize_behavior(
            who_compare=self.reference_mode1.time_series,
            compare_with='./StockAndFlowInPython/similarity_calculation/basic_behaviors.csv')
        self.lb_suggested_generic_stucture.config(text="Reference mode pattern: "+self.suggested_generic_structure)
        self.comparison_window1 = ComparisonWindow(self.comparison_figure)

    def load_generic_structure(self):
        self.session_handler1.apply_generic_structure(self.suggested_generic_structure)
        variables_in_model = list(self.session_handler1.model_structure.sfd.nodes)
        print("variables in model:", variables_in_model)
        print("structure name:", self.suggested_generic_structure)
        self.lb_name.config(text=self.suggested_generic_structure)
        self.variables_list['values'] = variables_in_model

    def generate_candidate_structure(self):
        """Generate a new candidate structure"""
        base = self.structure_manager.random_single()
        target = self.concept_manager.random_single()
        new = StructureUtilities.expand_structure(base_structure=base, target_structure=target)
        # print('    Generated new candidate structure:', new)
        self.structure_manager.derive_structure(base_structure=base, new_structure=new)

    def behavioral_similarity(self, who_compare, compare_with):
        # print("    Expansion: Calculating similarity...")

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
        new_base = copy.deepcopy(base_structure)
        print("    Base_structure: ", new_base.model_structure.sfd.nodes(data=True))

        # Base

        # get all elements in base structure
        base_structure_elements = list(new_base.model_structure.sfd.nodes)
        # pick an element from base_structure to start with. Now: randomly. Future: guided by activity.
        start_with_element_base = random.choice(base_structure_elements)
        print("    {} in base_structure is chosen to start with".format(start_with_element_base))
        print("    Details: ", new_base.model_structure.sfd.nodes[start_with_element_base])

        # get all in_edges into this element in base_structure
        in_edges_in_base = new_base.model_structure.sfd.in_edges(start_with_element_base)
        print("    In_edges in base_structure for {}".format(start_with_element_base),
              [in_edge_in_base[0] for in_edge_in_base in in_edges_in_base])

        # Target

        # get all elements in target structure
        target_structure_elements = list(target_structure.model_structure.sfd.nodes)

        # pick an element from target_structure to start with. Now: randomly. Future: guided by activity.
        start_with_element_target = random.choice(target_structure_elements)
        print("    {} in target_structure is chosen to start with".format(start_with_element_target))
        print("    Details: ", target_structure.model_structure.sfd.nodes[start_with_element_target])

        # get all in_edges into this element in target_structure
        in_edges_in_target = target_structure.model_structure.sfd.in_edges(start_with_element_target)
        # make sure the element to start with is not an end (boundary)
        while len(in_edges_in_target) == 0:
            start_with_element_target = random.choice(target_structure_elements)
            in_edges_in_target = target_structure.model_structure.sfd.in_edges(start_with_element_target)
        print("    In_edges in target_structure for {}".format(start_with_element_target),
              [in_edge_in_target[0] for in_edge_in_target in in_edges_in_target])

        # pick an in_edge from all in_edges into this element in target_structure
        chosen_in_edge_in_target = random.choice(list(in_edges_in_target))
        print("    In_edge chosen in target_structure: ", chosen_in_edge_in_target[0], '--->',
              chosen_in_edge_in_target[1])

        # Merge

        # extract the part of structure containing this in_edge in target_structure
        subgraph_from_target = target_structure.model_structure.sfd.edge_subgraph([chosen_in_edge_in_target])
        print("    Subgraph from target_structure:{} ".format(subgraph_from_target.nodes(data=True)))

        new_base.model_structure.sfd = nx.compose(new_base.model_structure.sfd, subgraph_from_target)
        print("New structure nodes:", new_base.model_structure.sfd.nodes.data())
        print("New structure edges:", new_base.model_structure.sfd.edges.data())

        return new_base


class StructureManager(object):
    """The class containing and managing all variants of structures"""

    def __init__(self):
        self.tree = nx.DiGraph()
        self.uid = 0
        self.tree_window = NewGraphNetworkWindow(self.tree, window_title="Expansion tree", x=750, y=50)
        self.candidate_structure_window = CandidateStructureWindow(self.tree)

    def generate_uid(self):
        """Get unique id for structure"""
        self.uid += 1
        return self.uid - 1

    def add_structure(self, structure):
        """Add a structure, usually as starting point"""
        self.tree.add_node(self.generate_uid(), structure=structure, activity=20)
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
                                node_match=iso.categorical_node_match(attr=['equation'], default=[None])
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
                                    node_match=iso.categorical_node_match(attr=['equation'], default=[None])
                                    # node_match=iso.categorical_node_match(attr=['equation', 'value'], default=[None, None])
                                    )
            if GM.is_isomorphic():
            # if nx.is_isomorphic(self.tree.nodes[neighbour]['structure'].model_structure.sfd, new_structure.model_structure.sfd):
                self.tree.nodes[neighbour]['activity'] += 1
                print("    The new structure already exists in base structure's neighbours")
                return

        # add a new node
        new_uid = self.generate_uid()
        print('    Deriving structure from {} to {}'.format(self.get_uid_by_structure(base_structure), new_uid))
        self.tree.add_node(new_uid,
                           structure=new_structure,
                           activity=self.tree.nodes[self.get_uid_by_structure(base_structure)]['activity']//ACTIVITY_DEMOMINATOR
                           )
        # build a link from the old structure to the new structure
        self.tree.add_edge(self.get_uid_by_structure(base_structure), new_uid)
        self.update_candidate_structure_window()

    def cool_down(self):
        """Update structures' activity (cooling down) after one iteration"""
        for u in self.tree.nodes:
            self.tree.nodes[u]['activity'] = self.tree.nodes[u]['activity'] - 1

    def random_single(self):
        """Return one structure"""
        random_structure_uid = random.choice(self.generate_distribution())
        print('    No. {} is chosen as base_structure;'.format(random_structure_uid))
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
        print('    {} is chosen as target_structure;'.format(random_concept_cld_name))
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
    def __init__(self, tree, width=1200, height=400, x=5, y=700):
        super().__init__()
        self.title("Display Candidate Structure")
        self.geometry("1200x400+5+750".format(width, height, x, y))

        self.selected_candidate_structure = None
        self.fm_select = Frame(self)
        self.fm_select.pack(side=LEFT)

        self.tree = tree

        self.fm_display_structure = Frame(self)
        self.fm_display_structure.configure(width=500)
        self.fm_display_structure.pack(side=LEFT)

        self.fm_display_behaviour = Frame(self)
        self.fm_display_behaviour.configure(width=500)
        self.fm_display_behaviour.pack(side=LEFT)

        self.generate_candidate_structure_list()

    def generate_candidate_structure_list(self):
        self.candidate_structure_list = Listbox(self.fm_select)
        self.candidate_structure_list.configure(width=10, height=20)
        self.candidate_structure_list.pack(side=TOP)
        for u in list(self.tree.nodes):
            # print("adding entry", u)
            self.candidate_structure_list.insert(END, u)
        self.candidate_structure_list.bind('<<ListboxSelect>>', self.display_candidate)

    def display_candidate(self, evt):
        self.display_candidate_structure()
        self.display_candidate_behaviour()

    def display_candidate_structure(self):
        selected_entry = self.candidate_structure_list.get(self.candidate_structure_list.curselection())
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

        selected_entry = self.candidate_structure_list.get(self.candidate_structure_list.curselection())
        self.selected_candidate_structure = self.tree.nodes[selected_entry]['structure']

        self.selected_candidate_structure.simulation_handler(25)

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


class ReferenceMode(object):
    """Class for Reference Mode"""
    def __init__(self, filename):
        self.case_numerical_data_filename = filename
        self.case_numerical_data = pd.read_csv(self.case_numerical_data_filename)
        self.time_series = np.array(self.case_numerical_data["stock0"].tolist()).reshape(-1, 1)
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
    def __init__(self, time_series, time_series_name, width=500, height=430, x=200, y=50):
        self.top = Toplevel()
        self.top.title("Reference Mode")
        self.top.geometry("{}x{}+{}+{}".format(width, height, x, y))
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
    root.geometry("+5+50")
    root.wm_title("Expansion Test")
    root.configure(background='#fff')
    ExpansionTest(root)
    root.mainloop()


if __name__ == '__main__':
    main()
