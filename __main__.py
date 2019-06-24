from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config import ITERATION_TIMES, ACTIVITY_DEMOMINATOR, INITIAL_LIKELIHOOD, INITIAL_ACTIVITY, REFERENCE_MODE_PATH, \
    COOL_DOWN_TIMES, COOL_DOWN_SWITCH, GENERIC_STRUCTURE_LIKELIHOOD_UPDATE_TIMES, \
    CANDIDATE_STRUCTURE_ACTIVITY_UPDATE_TIMES, \
    PURGE_SWITCH, PURGE_THRESHOLD
from StockAndFlowInPython.session_handler import SessionHandler, SFDWindow, GraphNetworkWindow, NewGraphNetworkWindow
from StockAndFlowInPython.structure_utilities.structure_utilities import new_expand_structure, create_causal_link, \
    apply_a_concept_cld, optimize_parameters
from StockAndFlowInPython.behaviour_utilities.behaviour_utilities import similarity_calc_pattern, categorize_behavior
from StockAndFlowInPython.graph_sd.graph_based_engine import function_names, STOCK, FLOW, VARIABLE, \
    PARAMETER, CONNECTOR, ALIAS, MULTIPLICATION, LINEAR, SUBTRACTION, DIVISION, ADDITION
from StockAndFlowInPython.sfd_canvas.sfd_canvas import SFDCanvas
from StockAndFlowInPython.parsing.XMILE_parsing import equation_to_text, text_to_equation
import pandas as pd
import numpy as np
import networkx as nx
import networkx.algorithms.isomorphism as iso
import matplotlib.pyplot as plt
import random
import time


class ExpansionPanel(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(width=300)
        self.pack(fill=BOTH, expand=1)

        # Menu

        self.menubar = Menu(self.master)

        self.file_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='File', menu=self.file_menu)
        self.file_menu.add_command(label='Quit', command=self.quit)

        self.reference_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='Reference', menu=self.reference_menu)
        self.reference_menu.add_command(label='Add reference mode', command=self.load_reference_mode_from_file)

        self.action_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='Action', menu=self.action_menu)
        self.action_menu.add_command(label='Expansion loop', command=self.expansion_loop)

        self.master.config(menu=self.menubar)

        # Control bar

        self.control_bar = LabelFrame(self.master, text='Expansion Control', font=5)
        self.control_bar.pack(side=TOP, anchor='w', fill=BOTH)

        self.btn_start_expansion = Button(self.control_bar, text='Start', command=self.expansion_loop)
        self.btn_start_expansion.pack(side=LEFT)

        self.btn_build_element_for_ref_mode = Button(self.control_bar, text='Build ref mode', command=self.build_element_for_reference_modes)
        self.btn_build_element_for_ref_mode.pack(side=LEFT)

        # self.btn_pause_expansion = Button(self.control_bar, text='Pause', command=self.pause_expansion)
        # self.btn_pause_expansion.pack(side=LEFT)
        #
        # self.btn_resume_expansion = Button(self.control_bar, text='Resume', command=self.resume_expansion)
        # self.btn_resume_expansion.pack(side=LEFT)

        # Bulletin board
        self.bulletin_board = LabelFrame(self.master, text='Information', font=5)
        self.bulletin_board.pack(side=TOP, anchor='w', fill=BOTH)

        self.lb_iteration_round = Label(self.bulletin_board, text='Iter', font=10)
        self.lb_iteration_round.pack(side=LEFT)

        # # Pause_resume control flag
        # self.if_loop_paused = True

        # Initialize concept CLDs
        self.concept_cld_manager = ConceptCLDManager()

        # Initialize generic structures
        self.generic_structure_manager = GenericStructureManager()

        # Initial expansion tree
        self.expansion_tree = nx.DiGraph()

        # Initialize structure manager
        self.structure_manager = StructureManager(tree=self.expansion_tree)

        # Reference modes
        self.reference_modes = dict()  # name : [type, time_series]
        self.reference_mode_bindings = dict()  # reference_mode_name : uid

        # Initialize reference mode manager
        self.reference_mode_manager = ReferenceModeManager(reference_modes=self.reference_modes,
                                                           reference_modes_binding=self.reference_mode_bindings)

        # Initialize binding manager
        self.binding_manager = BindingManager(reference_modes=self.reference_modes,
                                              reference_modes_binding=self.reference_mode_bindings,
                                              tree=self.expansion_tree)

        # TODO this task list will be the predecessor of 'Code Rack'
        # Initialize task list
        self.task_list = [3]

        # TODO test
        self.load_reference_mode_from_file()

        # Add a root structure
        structure_initial = SessionHandler()
        self.structure_manager.add_structure(structure=structure_initial)
        self.binding_manager.update_combobox()

        # Reset generic structure's likelihood
        self.generic_structure_manager.reset_all_likelihood()

        # Reset
        self.generic_structure_manager.generate_distribution()

        # Build element for each newly added reference mode in root structure
        self.build_element_for_reference_modes()

        # TODO: Check if all reference modes are built into all candidate structures. This is to allow that once adding
        #  a new reference mode, all candidate structures can have this new ref mode's variable added.

        # Specify round to iterate
        self.iteration_time = ITERATION_TIMES

        # self.expansion_loop()

    # TODO this is the basis for one agent's routine in the future
    def expansion_loop(self):

        i = 1
        while i <= self.iteration_time:
            print('\n\nExpansion: Iterating {}'.format(i))
            self.lb_iteration_round.configure(text='Iter ' + str(i))
            self.lb_iteration_round.update()

            # STEP: adjust generic structures' likelihood
            for j in range(GENERIC_STRUCTURE_LIKELIHOOD_UPDATE_TIMES):
                self.update_generic_structures_likelihood()

            # STEP: structural modification
            chosen_task = random.choice(self.task_list)
            if chosen_task == 1:
                """Generate a new candidate structure"""
                base = self.structure_manager.random_single()
                target = self.generic_structure_manager.random_single()
                # get all elements in base structure
                base_structure_elements = list(base.model_structure.sfd.nodes)
                # pick an element from base_structure to start with. Now: randomly. Future: guided by activity.
                start_with_element_base = random.choice(base_structure_elements)
                new = new_expand_structure(base_structure=base,
                                           start_with_element_base=start_with_element_base,
                                           target_structure=target)
                # new = expand_structure(base_structure=base, target_structure=target)
                self.structure_manager.derive_structure(base_structure=base, new_structure=new)
                self.task_list.append(random.choice([1, 2]))

            elif chosen_task == 2:
                """Create a new causal link in an existing candidate structure"""
                base = self.structure_manager.random_single()
                new = create_causal_link(base_structure=base)
                self.structure_manager.derive_structure(base_structure=base, new_structure=new)
                self.task_list.append(random.choice([1, 2]))

            elif chosen_task == 3:
                """Expand a candidate structure following a concept CLD"""
                # categorise a reference mode into a dynamic pattern. Temporarily only consider stock's ref mode
                stock_ref_names = list()
                for ref_name, ref_property in self.reference_modes.items():
                    if ref_property[0] == STOCK:
                        stock_ref_names.append(ref_name)
                print("    Currently we have stock ref modes:", stock_ref_names)
                chosen_stock_ref_name = random.choice(stock_ref_names)
                chosen_stock_uid = self.reference_mode_bindings[chosen_stock_ref_name]
                print("    We choose {}, uid {} as the beginning stock".format(chosen_stock_ref_name, chosen_stock_uid))
                pattern_name = self.categorize(behavior=self.reference_modes[chosen_stock_ref_name][1])

                # fetch concept CLD based on pattern
                concept_cld = self.concept_cld_manager.get_concept_cld_by_name(concept_cld_name=pattern_name)
                print(concept_cld.nodes(data=True))

                base = self.structure_manager.random_single()
                # TODO: this is not purely random
                target = self.generic_structure_manager.random_single()
                new = apply_a_concept_cld(base_structure=base,
                                          stock_uid_in_base_to_start_with=chosen_stock_uid,
                                          concept_cld=concept_cld,
                                          target_structure=target)
                self.structure_manager.derive_structure(base_structure=base, new_structure=new)
                self.task_list.append(4)

            elif chosen_task == 4:
                """Optimize parameters in a candidate structure"""
                base = self.structure_manager.random_single()

                new = optimize_parameters(base_structure=base,
                                          reference_modes=self.reference_modes,
                                          reference_mode_bindings=self.reference_mode_bindings)
                self.structure_manager.derive_structure(base_structure=base, new_structure=new)
                self.task_list.append(3)

            # STEP: adjust candidate structures' activity
            for k in range(CANDIDATE_STRUCTURE_ACTIVITY_UPDATE_TIMES):
                self.update_candidate_structure_activity_by_behavior()

            # STEP: cool down those not simulatable structures
            if COOL_DOWN_SWITCH:
                for k in range(COOL_DOWN_TIMES):
                    self.structure_manager.cool_down()

            # STEP: purge low activity structures
            if PURGE_SWITCH:
                self.structure_manager.purge_low_activity_structures()

            # STEP: sort candidate structures by activity
            # TODO: control this not only by number
            if i > 4:  # get enough candidate structures to sort
                self.structure_manager.sort_by_activity()

            # global display updates needed
            self.binding_manager.update_combobox()
            i += 1

    def load_reference_mode_from_file(self):
        self.reference_mode_manager.load_reference_mode_from_file()

    def build_element_for_reference_modes(self):
        # Get the first (also only) structure from expansion tree
        structure = self.structure_manager.tree.nodes[list(self.structure_manager.tree.nodes)[0]]['structure']
        for reference_mode_name, reference_mode_properties in self.reference_modes.items():
            # some ref mode may have been built, so we need to check with bindings.
            if reference_mode_name not in self.reference_mode_bindings.keys():  # not yet built
                if reference_mode_properties[0] == STOCK:
                    uid = structure.build_stock(name=reference_mode_name, initial_value=reference_mode_properties[1][0],
                                                x=213,
                                                y=174)
                elif reference_mode_properties[0] == FLOW:
                    uid = structure.build_flow(name=reference_mode_name, equation=0, x=302, y=171, points=[[236, 171], [392, 171]])
                elif reference_mode_properties[0] in [VARIABLE, PARAMETER]:
                    uid = structure.build_aux(name=reference_mode_name, equation=0, x=302, y=278)
                self.reference_mode_bindings[reference_mode_name] = uid
                self.binding_manager.generate_binding_list_box()
        structure.simulation_handler(25)

        self.structure_manager.if_can_simulate[self.structure_manager.get_current_candidate_structure_uid()] = True

    def update_candidate_structure_activity_by_behavior(self):
        if len(self.structure_manager.those_can_simulate) > 2:  # when there are more than 2 simulable candidates
            # Make more comparisons as there are more candidate structures
            iter_times = len(self.structure_manager.those_can_simulate) // 2
            for i in range(iter_times):
                # Get 2 random candidates
                random_two_candidates = [None, None]
                while random_two_candidates[0] == random_two_candidates[1]:
                    # Here we don't use the weighted random pair, to give those less active more opportunity
                    random_two_candidates = self.structure_manager.random_pair_even()
                    while not (self.structure_manager.if_can_simulate[random_two_candidates[0]] and
                               self.structure_manager.if_can_simulate[random_two_candidates[1]]):
                        # we have to get two simulatable structures to compare their behaviors
                        random_two_candidates = self.structure_manager.random_pair_even()
                print("    Two candidate structures chosen for comparison: ", random_two_candidates)
                # Calculate their similarity to reference mode
                candidate_0_distance = 0
                candidate_1_distance = 0
                s_uid_0 = random_two_candidates[0]
                s_uid_1 = random_two_candidates[1]
                for reference_mode_name, reference_mode_property in self.reference_modes.items():
                    uid = self.reference_mode_bindings[reference_mode_name]
                    candidate_0_distance += self.behavioral_distance(
                        self.structure_manager.tree.nodes[s_uid_0]['structure'].model_structure.get_element_by_uid(uid)[
                            'value'],
                        reference_mode_property[1]
                    )
                    candidate_1_distance += self.behavioral_distance(
                        self.structure_manager.tree.nodes[s_uid_1]['structure'].model_structure.get_element_by_uid(uid)[
                            'value'],
                        reference_mode_property[1]
                    )

                print(candidate_0_distance, candidate_1_distance)
                # Update their activity
                if candidate_0_distance != candidate_1_distance:
                    if candidate_0_distance > candidate_1_distance:
                        self.structure_manager.update_activity_elo(s_uid_1, s_uid_0)
                    else:
                        self.structure_manager.update_activity_elo(s_uid_0, s_uid_1)
                # print("All nodes' activity:", self.structure_manager.show_all_activity())

    def update_generic_structures_likelihood(self):
        random_two_generic_structures = [None, None]
        while random_two_generic_structures[0] == random_two_generic_structures[1]:  # The two cannot be the same
            random_two_generic_structures = self.generic_structure_manager.random_pair()
        generic_structure_0 = random_two_generic_structures[0]
        generic_structure_1 = random_two_generic_structures[1]
        # print(random_two_generic_structures)
        # TODO this part is important: assessment of a generic structure's likelihood.

        # randomly choose a reference mode
        chosen_reference_mode = random.choice(list(self.reference_modes.keys()))
        chosen_reference_mode_type = self.reference_modes[chosen_reference_mode][0]

        # randomly choose element from generic_structures
        chosen_element_from_generic_structure_0 = random.choice(
            self.generic_structure_manager.generic_structures[generic_structure_0].model_structure.all_certain_type(
                chosen_reference_mode_type))
        chosen_element_from_generic_structure_1 = random.choice(
            self.generic_structure_manager.generic_structures[generic_structure_1].model_structure.all_certain_type(
                chosen_reference_mode_type))

        random_two_generic_structures_distance = {
            generic_structure_0: self.behavioral_distance(
                self.generic_structure_manager.generic_structures[generic_structure_0].model_structure.sfd.node[
                    chosen_element_from_generic_structure_0]['value'],
                self.reference_modes[chosen_reference_mode][1]),
            generic_structure_1: self.behavioral_distance(
                self.generic_structure_manager.generic_structures[generic_structure_1].model_structure.sfd.node[
                    chosen_element_from_generic_structure_1]['value'],
                self.reference_modes[chosen_reference_mode][1])
        }
        # print(random_two_generic_structures_distance)
        # a larger distance -> a lower likelihood
        if random_two_generic_structures_distance[random_two_generic_structures[0]] < \
                random_two_generic_structures_distance[random_two_generic_structures[1]]:
            self.generic_structure_manager.update_likelihood_elo(random_two_generic_structures[0],
                                                                 random_two_generic_structures[1])
        else:
            self.generic_structure_manager.update_likelihood_elo(random_two_generic_structures[1],
                                                                 random_two_generic_structures[0])
        print(self.generic_structure_manager.generic_structures_likelihood)

    def behavioral_distance(self, who_compare, compare_with):
        print("    Expansion: Calculating similarity...")
        distance, comparison_figure = similarity_calc_pattern(np.array(who_compare).reshape(-1, 1),
                                                              np.array(compare_with).reshape(-1, 1))
        # ComparisonWindow(comparison_figure)
        return distance

    def categorize(self, behavior):
        print("    Expansion: Categorizing a behavior...")
        pattern, comparison_figure = categorize_behavior(np.array(behavior).reshape(-1, 1))
        # ComparisonWindow(comparison_figure)
        return pattern


class ConceptCLDManager(object):
    def __init__(self):
        # TODO: this dictionary will become another network in the future
        self.concept_clds = dict()

        concept_cld_constant = nx.DiGraph()
        concept_cld_constant.add_node(STOCK)
        concept_cld_constant.graph['polarity'] = 'no'
        concept_cld_constant.graph['begin_with'] = STOCK
        concept_cld_constant.graph['end_with'] = STOCK
        self.concept_clds['constant'] = concept_cld_constant

        concept_cld_growth_a = nx.DiGraph()
        concept_cld_growth_a.add_nodes_from([STOCK, PARAMETER])
        concept_cld_growth_a.add_edge(PARAMETER, STOCK, polarity='positive')
        concept_cld_growth_a.graph['polarity'] = 'no'
        concept_cld_growth_a.graph['begin_with'] = STOCK
        concept_cld_growth_a.graph['end_with'] = STOCK
        self.concept_clds['growth_a'] = concept_cld_growth_a

        concept_cld_growth_b = nx.DiGraph()
        concept_cld_growth_b.add_nodes_from([STOCK, MULTIPLICATION])
        concept_cld_growth_b.add_edge(STOCK, MULTIPLICATION, polarity='positive')
        concept_cld_growth_b.add_edge(MULTIPLICATION, STOCK, polarity='positive')
        concept_cld_growth_b.graph['polarity'] = 'positive'
        concept_cld_growth_b.graph['begin_with'] = STOCK
        concept_cld_growth_b.graph['end_with'] = STOCK
        self.concept_clds['growth_b'] = concept_cld_growth_b

        concept_cld_decline_a = nx.DiGraph()
        concept_cld_decline_a.add_nodes_from([STOCK, PARAMETER])
        concept_cld_decline_a.add_edge(PARAMETER, STOCK, polarity='negative')
        concept_cld_decline_a.graph['polarity'] = 'no'
        concept_cld_decline_a.graph['begin_with'] = STOCK
        concept_cld_decline_a.graph['end_with'] = STOCK
        self.concept_clds['decline_a'] = concept_cld_decline_a

        concept_cld_decline_c = nx.DiGraph()
        concept_cld_decline_c.add_nodes_from([STOCK, SUBTRACTION, DIVISION])
        concept_cld_decline_c.add_edge(STOCK, SUBTRACTION, polarity='positive')
        concept_cld_decline_c.add_edge(SUBTRACTION, DIVISION, polarity='positive')
        concept_cld_decline_c.add_edge(DIVISION, STOCK, polarity='negative')
        concept_cld_decline_c.graph['polarity'] = 'negative'
        concept_cld_decline_c.graph['begin_with'] = STOCK
        concept_cld_decline_c.graph['end_with'] = STOCK
        self.concept_clds['decline_c'] = concept_cld_decline_c

    def get_concept_cld_by_name(self, concept_cld_name):
        for name, concept_cld in self.concept_clds.items():
            if name == concept_cld_name:
                return concept_cld


class ReferenceModeManager(Toplevel):
    def __init__(self, reference_modes, reference_modes_binding, reference_mode_path=REFERENCE_MODE_PATH, width=600,
                 height=400, x=5, y=200):
        super().__init__()
        self.title("Reference Mode Manager")
        self.geometry("{}x{}+{}+{}".format(width, height, x, y))

        self.reference_mode_path = reference_mode_path
        self.numerical_data = None
        self.time_series = dict()
        self.reference_modes = reference_modes
        self.reference_modes_binding = reference_modes_binding

        self.fm_select = Frame(self)
        self.fm_select.pack(side=LEFT, fill=Y)
        self.lb_select = Label(self.fm_select, text='Reference Modes', font=7)
        self.lb_select.pack(anchor='nw')

        self.fm_display = Frame(self)
        self.fm_display.pack(side=LEFT)

        self.fm_add_remove = Frame(self.fm_select)
        self.fm_add_remove.pack(side=BOTTOM)

        self.btn_remove = Button(self.fm_add_remove, text='Remove', command=self.remove_reference_mode)
        self.btn_remove.pack(side=RIGHT)

        self.btn_add = Button(self.fm_add_remove, text='Add', command=self.load_reference_mode_from_file)
        self.btn_add.pack(side=RIGHT)

        self.generate_reference_mode_list_box()

    def load_reference_mode_from_file(self):
        """
        The logic is: file -> file in memory (numerical data) -> time series --selection--> reference mode
        :return:
        """
        if self.reference_mode_path is None and len(self.time_series) == 0:  # either path not specified and no t-series
            self.get_reference_mode_file_name()
        self.numerical_data = pd.read_csv(self.reference_mode_path)
        for column in self.numerical_data:
            self.time_series[column] = self.numerical_data[column].tolist()
        select_dialog = SelectReferenceModeWindow(time_series=self.time_series, reference_modes=self.reference_modes)
        self.wait_window(select_dialog)  # important!
        # reference_mode_type = select_dialog.reference_mode_type
        # reference_mode_name = select_dialog.selected_reference_mode
        # if reference_mode_type is not None and reference_mode_name is not None:
        #     self.reference_modes[reference_mode_name] = [reference_mode_type, self.time_series[reference_mode_name]]
        #     print("Added reference mode for {} : {}".format(reference_mode_type, reference_mode_name))
        self.generate_reference_mode_list_box()

    def get_reference_mode_file_name(self):
        self.reference_mode_path = filedialog.askopenfilename()

    def generate_reference_mode_list_box(self):
        try:
            self.reference_mode_list_box.destroy()
        except AttributeError:
            pass
        self.reference_mode_list_box = Listbox(self.fm_select, width=15, height=20)
        self.reference_mode_list_box.pack(side=TOP, fill=Y)

        for ref_mode in self.reference_modes.keys():
            self.reference_mode_list_box.insert(END, ref_mode)
        self.reference_mode_list_box.bind('<<ListboxSelect>>', self.show_reference_mode)

    def show_reference_mode(self, evt=None):
        try:
            self.reference_mode_graph.get_tk_widget().destroy()
        except AttributeError:
            pass
        self.reference_mode_figure = Figure(figsize=(5, 4))
        self.reference_mode_plot = self.reference_mode_figure.add_subplot(111)
        self.reference_mode_plot.plot(
            self.time_series[self.reference_mode_list_box.get(self.reference_mode_list_box.curselection())], '*')
        self.reference_mode_plot.set_xlabel("Time")
        self.reference_mode_plot.set_ylabel(
            self.reference_mode_list_box.get(self.reference_mode_list_box.curselection()))
        self.reference_mode_graph = FigureCanvasTkAgg(self.reference_mode_figure, master=self.fm_display)
        self.reference_mode_graph.draw()
        self.reference_mode_graph.get_tk_widget().pack(side=LEFT)

    def remove_reference_mode(self):
        # get selected ref mode
        selected_reference_mode = self.reference_mode_list_box.get(self.reference_mode_list_box.curselection())

        # remove this reference mode from 1. ref mode list 2. binding list
        self.reference_modes.pop(selected_reference_mode)
        self.reference_modes_binding.pop(selected_reference_mode)
        self.generate_reference_mode_list_box()
        self.show_reference_mode()


class SelectReferenceModeWindow(Toplevel):
    def __init__(self, time_series, reference_modes, width=600, height=400, x=300, y=200):
        super().__init__()
        self.title("Select Reference Mode...")
        self.geometry("{}x{}+{}+{}".format(width, height, x, y))
        self.time_series = time_series
        self.reference_modes = reference_modes
        # self.selected_reference_mode = None
        # self.reference_mode_type = None

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
        self.confirm_button = Button(self.fm_buttons, text='Add', command=self.confirm)
        self.confirm_button.pack(side=LEFT, anchor='center')
        self.close_button = Button(self.fm_buttons, text='Close', command=self.close)
        self.close_button.pack(side=LEFT, anchor='center')

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
        reference_mode_type = self.ref_md_type.get()
        selected_reference_mode = self.time_series_list.get(self.time_series_list.curselection())
        if reference_mode_type is not None and selected_reference_mode is not None:
            self.reference_modes[selected_reference_mode] = [reference_mode_type, self.time_series[selected_reference_mode]]
            print("Added reference mode for {} : {}".format(reference_mode_type, selected_reference_mode))

    def close(self):
        self.destroy()


class BindingManager(Toplevel):
    def __init__(self, reference_modes, reference_modes_binding, tree, width=600, height=400, x=650, y=200):
        super().__init__()
        self.title("Binding Manager")
        self.geometry("{}x{}+{}+{}".format(width, height, x, y))
        self.reference_modes = reference_modes
        self.reference_modes_binding = reference_modes_binding
        self.tree = tree

        self.selected_structure = 0
        self.selected_variable = None
        self.selected_reference_mode = None

        self.fm_actions = Frame(self)
        self.fm_actions.pack(side=TOP, fill=X)

        # TODO using Tkinter it is not possible to do this refresh. Going to be replaced by signal-slot in future.
        self.btn_refresh = Button(self.fm_actions, text='Refresh', command=self.update_combobox)
        self.btn_refresh.pack(side=LEFT)

        self.btn_add_binding = Button(self.fm_actions, text='Add binding', command=self.add_binding)
        self.btn_add_binding.pack(side=LEFT)

        self.btn_remove_binding = Button(self.fm_actions, text='Remove binding', command=self.remove_binding)
        self.btn_remove_binding.pack(side=LEFT)

        # Left hand side

        self.fm_list = LabelFrame(self, text='Bindings')
        self.fm_list.pack(side=LEFT, fill=Y)

        self.generate_binding_list_box()

        self.fm_display_and_browse = Frame(self)
        self.fm_display_and_browse.pack(side=RIGHT, fill=BOTH, expand=True)

        # Right hand side

        self.fm_display_details = LabelFrame(self.fm_display_and_browse, text='Binding Details')
        self.fm_display_details.pack(side=TOP, fill=BOTH)

        self.lb_binding_details = Label(self.fm_display_details, text='Select a binding to view details')
        self.lb_binding_details.pack(side=TOP, anchor='w')

        self.fm_browse_element = LabelFrame(self.fm_display_and_browse, text='Browse structure element')
        self.fm_browse_element.pack(side=TOP, fill=BOTH)

        self.structure_list = ttk.Combobox(self.fm_browse_element)
        self.structure_list["values"] = ['structure']
        self.structure_list.current(0)
        self.structure_list.bind("<<ComboboxSelected>>", self.select_structure)
        self.structure_list.pack(side=LEFT)

        self.variable_list = ttk.Combobox(self.fm_browse_element)
        self.variable_list["values"] = ['variable']
        self.variable_list.current(0)
        self.variable_list.bind("<<ComboboxSelected>>", self.select_variable)
        self.variable_list.pack(side=LEFT)

        self.fm_browse_reference_mode = LabelFrame(self.fm_display_and_browse, text='Browse reference mode')
        self.fm_browse_reference_mode.pack(side=TOP, fill=BOTH)

        self.reference_mode_list = ttk.Combobox(self.fm_browse_reference_mode)
        self.reference_mode_list["values"] = ['reference mode']
        self.reference_mode_list.current(0)
        self.reference_mode_list.bind("<<ComboboxSelected>>", self.select_reference_mode)
        self.reference_mode_list.pack(side=LEFT)

    def add_binding(self):
        if self.selected_reference_mode is not None:
            if self.selected_variable is not None:
                # print("Here!", self.tree.nodes[int(self.selected_structure)]['structure'].model_structure.sfd.nodes(data=True))
                self.reference_modes_binding[self.selected_reference_mode] = \
                self.tree.nodes[int(self.selected_structure)]['structure'].model_structure.sfd.nodes[
                    self.selected_variable]['uid']
                self.generate_binding_list_box()
            else:
                print("Please select a variable.")
        else:
            print("Please select a reference mode.")

    def remove_binding(self):
        selected_ref_name = self.binding_list_box.get(self.binding_list_box.curselection())
        bound_element_name = self.get_binding_element_name_by_ref_name(selected_ref_name)
        self.reference_modes_binding.pop(selected_ref_name)
        print("Removed binding between ref mode '{}' and variable '{}'".format(selected_ref_name, bound_element_name))
        self.generate_binding_list_box()

    def get_binding_element_name_by_ref_name(self, ref_name=None):
        if ref_name is None:
            ref_name = self.binding_list_box.get(self.binding_list_box.curselection())
        selected_binding_element_uid = self.reference_modes_binding[ref_name]
        selected_binding_element_name = self.tree.nodes[int(self.selected_structure)]['structure'].model_structure. \
            get_element_name_by_uid(selected_binding_element_uid)
        return selected_binding_element_name

    def select_structure(self, *args):
        self.selected_structure = self.structure_list.get()
        # print("structure {} is selected.".format(self.selected_structure))
        self.update_combobox()

    def select_variable(self, *args):
        self.selected_variable = self.variable_list.get()
        self.update_combobox()

    def select_reference_mode(self, *args):
        self.selected_reference_mode = self.reference_mode_list.get()
        self.update_combobox()

    def generate_binding_list_box(self):
        try:
            self.binding_list_box.destroy()
        except AttributeError:
            pass
        self.binding_list_box = Listbox(self.fm_list, width=15)
        self.binding_list_box.pack(side=LEFT, fill=Y)

        for ref_mode in self.reference_modes_binding.keys():
            self.binding_list_box.insert(END, ref_mode)
        self.binding_list_box.bind('<<ListboxSelect>>', self.show_binding_details)

    def show_binding_details(self, evt):
        self.update_combobox()
        selected_binding_name = self.binding_list_box.get(self.binding_list_box.curselection())
        selected_binding_element_uid = self.reference_modes_binding[selected_binding_name]
        print()
        print("Hereeee", self.tree.nodes(data=True))
        selected_binding_element_name = self.tree.nodes[int(self.selected_structure)]['structure'].model_structure. \
            get_element_name_by_uid(selected_binding_element_uid)
        detail_text = "Ref mode: {} ; Element No.{}, {}".format(selected_binding_name,
                                                                selected_binding_element_uid,
                                                                selected_binding_element_name)
        self.lb_binding_details.configure(text=detail_text)
        self.lb_binding_details.update()

    def update_combobox(self):
        # print('updating combobox')
        try:
            structures = list(self.tree.nodes)
        except:
            structures = ['structure']
        self.structure_list["values"] = structures

        # This int() is very important, because what get() from combobox is 'str.
        try:
            variables_in_selected_structure = list(
                self.tree.nodes[int(self.selected_structure)]['structure'].model_structure.sfd.nodes)
        except KeyError:
            # print("key error")
            variables_in_selected_structure = ['variable']
        self.variable_list["values"] = variables_in_selected_structure

        reference_mode_names = list(self.reference_modes.keys())
        self.reference_mode_list["values"] = reference_mode_names


class StructureManager(object):
    """The class containing and managing all variants of structures"""

    def __init__(self, tree):
        self.tree = tree
        self.candidate_structure_uid = 0
        self.sorted_tree = list()
        self.candidate_structure_window = CandidateStructureWindow(tree=self.tree, sorted_tree=self.sorted_tree)
        self.if_can_simulate = dict()
        self.those_can_simulate = list()
        self.those_cannot_simulate = list()

    def sort_by_activity(self):
        # sort all candidate structures by activity
        self.sorted_tree = sorted(list(self.tree.nodes(data='activity')), key=lambda x: x[1], reverse=True)
        print('Sorted tree:', self.sorted_tree)
        string = ''
        for i in range(3):
            string += str(self.sorted_tree[i][0]) + '[{}] '.format(self.sorted_tree[i][1])
        self.candidate_structure_window.label_top_three_0.configure(text=string)
        self.candidate_structure_window.label_top_three_0.update()

    def show_all_activity(self):
        all_activity = nx.get_node_attributes(self.tree, 'activity')
        return all_activity

    def get_new_candidate_structure_uid(self):
        """Get unique id for structure"""
        self.candidate_structure_uid += 1
        return self.candidate_structure_uid

    def get_current_candidate_structure_uid(self):
        return self.candidate_structure_uid

    def add_structure(self, structure):
        """Add a structure, usually as starting point"""
        self.tree.add_node(self.get_new_candidate_structure_uid(), structure=structure, activity=INITIAL_ACTIVITY)
        self.update_candidate_structure_window()

    def get_uid_by_structure(self, structure):
        # print(self.tree.nodes(data=True))
        for u in list(self.tree.nodes):
            if self.tree.nodes[u]['structure'] == structure:
                return u
        print(
            '    StructureManager: Can not find uid for given structure {}.'.format(structure))

    def derive_structure(self, base_structure, new_structure):
        """Derive a new structure from an existing one"""
        # decide if this new_structure has been generated before. if so: confirm activity. if not: confirm it.
        # 1. identical to base_structure it self
        # if nx.is_isomorphic(base_structure.model_structure.sfd, new_structure.model_structure.sfd):
        GM = iso.DiGraphMatcher(base_structure.model_structure.sfd, new_structure.model_structure.sfd,
                                node_match=iso.categorical_node_match(attr=['function'],
                                                                      # attr=['equation', 'value'],
                                                                      default=[None],
                                                                      # default=[None, None]
                                                                      )
                                )
        if GM.is_isomorphic():
            self.tree.nodes[self.get_uid_by_structure(base_structure)]['activity'] += 1
            print("    The new structure is identical to the base structure")
            return
        # 2. identical to a neighbor of the base_structure
        for neighbour in self.tree.neighbors(self.get_uid_by_structure(base_structure)):
            GM = iso.DiGraphMatcher(self.tree.nodes[neighbour]['structure'].model_structure.sfd,
                                    new_structure.model_structure.sfd,
                                    node_match=iso.categorical_node_match(attr=['function', 'flow_from', 'flow_to'],
                                                                          # attr=['equation', 'value'],
                                                                          default=[None, None, None],
                                                                          # default=[None, None]
                                                                          )
                                    )
            if GM.is_isomorphic():
                # if nx.is_isomorphic(self.tree.nodes[neighbour]['structure'].model_structure.sfd, new_structure.model_structure.sfd):
                self.tree.nodes[neighbour]['activity'] += 1
                # print(self.tree.nodes[neighbour]['structure'].model_structure.sfd.nodes(data=True))
                # print(new_structure.model_structure.sfd.nodes(data=True))
                print("    The new structure already exists in base structure's neighbours")
                return

        # confirm a new node
        new_uid = self.get_new_candidate_structure_uid()
        print('    Deriving structure from {} to {}'.format(self.get_uid_by_structure(base_structure), new_uid))
        new_activity = self.tree.nodes[self.get_uid_by_structure(base_structure)]['activity'] // ACTIVITY_DEMOMINATOR
        self.tree.add_node(new_uid,
                           structure=new_structure,
                           activity=new_activity
                           )

        # subtraction this part of activity from the base_structure
        self.tree.nodes[self.get_uid_by_structure(base_structure)]['activity'] -= new_activity
        if self.tree.nodes[self.get_uid_by_structure(base_structure)]['activity'] < 1:
            self.tree.nodes[self.get_uid_by_structure(base_structure)]['activity'] = 1

        # build a link from the old structure to the new structure
        self.tree.add_edge(self.get_uid_by_structure(base_structure), new_uid)
        # simulate this new structure

        new_structure.simulation_handler(25)

        # TODO decide if this part still needs to be kept, for all candidate structures are supposed to be simulatable.
        try:
            new_structure.simulation_handler(25)
            self.if_can_simulate[new_uid] = True
            self.those_can_simulate.append(new_uid)
        except KeyError:
            self.if_can_simulate[new_uid] = False
            self.those_cannot_simulate.append(new_uid)

        print("Simulatable structures:", self.if_can_simulate)

        self.update_candidate_structure_window()

    def cool_down(self):
        """Cool down structures"""
        for u in self.tree.nodes:  # no matter it is simulatable or not
            # for u in self.those_cannot_simulate:
            self.tree.nodes[u]['activity'] = self.tree.nodes[u]['activity'] - 1 if self.tree.nodes[u][
                                                                                       'activity'] > 1 else 1
        self.update_candidate_structure_window()

    def random_single(self):
        """Return one structure"""
        random_structure_uid = random.choice(self.generate_distribution_weighted())
        print('\n    No.{} is chosen as base_structure;\n'.format(random_structure_uid))
        return self.tree.nodes[random_structure_uid]['structure']

    def random_pair_weighted(self):
        """Return a pair of structures for competition"""
        random_structures_uid = random.choices(self.generate_distribution_weighted(), k=2)
        return random_structures_uid

    def random_pair_even(self):
        random_structures_uid = random.choices(list(self.tree.nodes), k=2)
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
        k = 8
        r_winner = r_winner + k * (gain_winner - e_winner)
        r_loser = r_loser + k * (gain_loser - e_loser)

        def normalize(r):
            if r > 50:
                r = 50
            elif r < 1:
                r = 1
            return r

        self.tree.nodes[winner]['activity'] = round(normalize(r_winner))
        self.tree.nodes[loser]['activity'] = round(normalize(r_loser))

    def generate_distribution_weighted(self):
        """Generate a list, containing multiple uids of each structure with weighted distribution"""
        distribution_list = list()
        for u in list(self.tree.nodes):
            for i in range(self.tree.nodes[u]['activity']):
                distribution_list.append(u)
        return distribution_list

    def update_candidate_structure_window(self):
        self.candidate_structure_window.update_tree_display()
        self.candidate_structure_window.generate_candidate_structure_list()

    def purge_low_activity_structures(self):
        elements = list(self.tree.nodes)
        for element in elements:
            if self.tree.nodes[element]['activity'] <= PURGE_THRESHOLD:
                # TODO in the future, consider when edge has its attributes
                in_edges_to_element = self.tree.in_edges(element)
                print("In edges to 0 act ele:", in_edges_to_element)
                out_edges_from_element = self.tree.out_edges(element)
                print("Out edges from 0 act ele:", out_edges_from_element)
                for in_edge in in_edges_to_element:
                    for out_edge in out_edges_from_element:
                        self.tree.add_edge(in_edge[0], out_edge[1])
                self.tree.remove_node(element)
                print("Low activity structure {} is purged.".format(element))


class CandidateStructureWindow(Toplevel):
    def __init__(self, tree, sorted_tree, x=5, y=400):
        super().__init__()
        self.title("Candidate Structures")
        self.geometry("+{}+{}".format(x, y))

        self.tree = tree
        self.sorted_tree = sorted_tree
        self.tree_window = NewGraphNetworkWindow(self.tree, window_title="Expansion tree", node_color="skyblue",
                                                 width=550, height=550, x=1100, y=50, attr='activity')
        self.selected_candidate_structure = None

        # Top widgets

        self.fm_actions = Frame(self)
        self.fm_actions.pack(side=TOP, fill=BOTH)

        self.btn_accept = Button(self.fm_actions, text='Accept and keep', command=self.accept_a_structure)
        self.btn_accept.pack(side=LEFT)

        self.btn_modify = Button(self.fm_actions, text='Modify', command=self.modify_a_structure)
        self.btn_modify.pack(side=LEFT)

        # Middle widgets

        self.fm_middle = Frame(self)
        self.fm_middle.pack(side=TOP, fill=X)

        self.fm_select = Frame(self.fm_middle)
        self.fm_select.pack(side=LEFT)

        self.label_select = Label(self.fm_select, text='Candidate\nStructures', font=6)
        self.label_select.pack(anchor='nw')

        self.label_top_three_0 = Label(self.fm_select, text='', font=6)
        self.label_top_three_0.pack(side=BOTTOM, anchor='nw')
        self.label_top_three_1 = Label(self.fm_select, text='Top 3 \nCandidates:', font=6)
        self.label_top_three_1.pack(side=BOTTOM, anchor='nw')

        self.stock_and_flow_diagram = SFDCanvas(self.fm_middle)
        self.stock_and_flow_diagram.pack(side=LEFT)

        self.fm_display_behaviour = Frame(self.fm_middle)
        self.fm_display_behaviour.pack(side=LEFT)

        # Bottom widgets

        self.fm_display_structure_cld = Frame(self)
        self.fm_display_structure_cld.pack(side=TOP, fill=X)

        self.generate_candidate_structure_list()

        self.fm_logging = Frame(self)
        self.fm_logging.pack(side=BOTTOM)

    def update_tree_display(self):
        tree_node_color = list()
        if len(self.sorted_tree) > 3:  # when the sorted tree is generated
            top_three = [self.sorted_tree[0][0], self.sorted_tree[1][0], self.sorted_tree[2][0]]
            for element in self.tree.nodes:
                if element in top_three:
                    tree_node_color.append('orangered')
                else:
                    tree_node_color.append('skyblue')
        else:
            tree_node_color = 'skyblue'
        # print("HERE", tree_node_color)
        self.tree_window.update_graph_network(node_color=tree_node_color)

    def accept_a_structure(self):
        # get the selected structure (entry) from listbox
        selected_entry = self.candidate_structure_list_box.get(self.candidate_structure_list_box.curselection())

        # remove all other nodes from the tree
        elements = list(self.tree.nodes)
        elements.remove(selected_entry)
        self.tree.remove_nodes_from(elements)

        # regenerate list box
        self.generate_candidate_structure_list()

        # update tree display
        # TODO this needs mechanism like 'signal and slot', but Tkinter does not have. Will do in Qt.

    def modify_a_structure(self):
        # get the selected structure (entry) from listbox
        selected_entry = self.candidate_structure_list_box.get(self.candidate_structure_list_box.curselection())
        structure_modifier = StructureModifier(self.tree.nodes[selected_entry]['structure'])

    def generate_candidate_structure_list(self):
        try:
            self.candidate_structure_list_box.destroy()
            self.candidate_structure_list_scrollbar.destroy()
        except AttributeError:
            pass

        self.candidate_structure_list_box = Listbox(self.fm_select)
        self.candidate_structure_list_box.configure(width=10, height=20)
        self.candidate_structure_list_box.pack(side=LEFT)

        self.candidate_structure_list_scrollbar = Scrollbar(self.fm_select, orient="vertical")
        self.candidate_structure_list_scrollbar.config(command=self.candidate_structure_list_box.yview)
        self.candidate_structure_list_scrollbar.pack(side=RIGHT, fill=Y)

        for u in list(self.tree.nodes):
            # print("adding entry", u)
            self.candidate_structure_list_box.insert(END, u)
        self.candidate_structure_list_box.bind('<<ListboxSelect>>', self.display_candidate)

    def display_candidate(self, evt):
        self.display_candidate_structure_sfd()
        self.display_candidate_structure_cld()
        self.display_candidate_behaviour()

    def display_candidate_structure_sfd(self):
        selected_entry = self.candidate_structure_list_box.get(self.candidate_structure_list_box.curselection())
        self.selected_candidate_structure = self.tree.nodes[selected_entry]['structure']

        self.stock_and_flow_diagram.reset_canvas()
        self.stock_and_flow_diagram.draw_sfd(self.selected_candidate_structure.model_structure.sfd)

    def display_candidate_structure_cld(self):
        selected_entry = self.candidate_structure_list_box.get(self.candidate_structure_list_box.curselection())
        self.selected_candidate_structure = self.tree.nodes[selected_entry]['structure']

        try:
            plt.close()
            self.candidate_structure_cld_canvas.get_tk_widget().destroy()
        except:
            pass
        fig, ax = plt.subplots(figsize=(11, 9))

        node_attrs_function = nx.get_node_attributes(self.selected_candidate_structure.model_structure.sfd, 'function')
        node_attrs_value = nx.get_node_attributes(self.selected_candidate_structure.model_structure.sfd, 'value')
        custom_node_labels = dict()
        for node, attr in node_attrs_function.items():
            # when the element only has a value but no function
            if attr is None:
                attr = node_attrs_value[node][0]
            # when the element has a function
            else:
                # attr = [attr[0]] + [factor for factor in attr[1:]]
                attr = equation_to_text(attr)
            custom_node_labels[node] = "{}={}".format(node, attr)

        edge_attrs_polarity = nx.get_edge_attributes(self.selected_candidate_structure.model_structure.sfd, 'polarity')
        custom_edge_colors = list()
        for edge, attr in edge_attrs_polarity.items():
            color = 'k'  # black
            if attr == 'negative':
                color = 'b'  # blue
            custom_edge_colors.append(color)

        nx.draw_networkx(G=self.selected_candidate_structure.model_structure.sfd,
                         labels=custom_node_labels,
                         font_size=10,
                         node_color='skyblue',
                         edge_color=custom_edge_colors)
        plt.axis('off')  # turn off axis for structure display
        self.candidate_structure_cld_canvas = FigureCanvasTkAgg(figure=fig, master=self.fm_display_structure_cld)
        self.candidate_structure_cld_canvas.get_tk_widget().configure(height=450)
        self.candidate_structure_cld_canvas.get_tk_widget().pack(side=LEFT)

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

        result_figure = self.selected_candidate_structure.model_structure.draw_results(
            # names=['stock0'],
            rtn=True)
        self.simulation_result_canvas = FigureCanvasTkAgg(figure=result_figure, master=self.fm_display_behaviour)
        self.simulation_result_canvas.get_tk_widget().configure(height=400, width=500)
        self.simulation_result_canvas.get_tk_widget().pack(side=LEFT)

        # Display result
        self.update()


class StructureModifier(Toplevel):
    def __init__(self, structure, width=1250, height=450, x=5, y=300):
        super().__init__()
        self.title("Structure Modifier")
        self.geometry("+{}+{}".format(x, y))
        self.structure = structure
        self.variables_in_model = list(self.structure.model_structure.sfd.nodes)

        # Actions

        self.fm_actions = Frame(self, width=100)
        self.fm_actions.pack(side=LEFT, fill=Y)

        self.btn_refresh = Button(self.fm_actions, text='Refresh', command=self.refresh_display_structure)
        self.btn_refresh.pack(side=TOP, anchor='w')

        # Add

        self.fm_actions_add = LabelFrame(self.fm_actions, text='Add')
        self.fm_actions_add.pack(side=TOP, anchor='w', fill=X)

        self.btn_add_stock = Button(self.fm_actions_add, text='Stock', command=self.add_stock)
        self.btn_add_stock.pack(side=TOP, anchor='w')

        self.btn_add_flow = Button(self.fm_actions_add, text='Flow', command=self.add_flow)
        self.btn_add_flow.pack(side=TOP, anchor='w')

        self.btn_add_aux = Button(self.fm_actions_add, text='Auxiliary', command=self.add_variable)
        self.btn_add_aux.pack(side=TOP, anchor='w')

        self.btn_add_connector = Button(self.fm_actions_add, text='Connector', command=self.add_connector)
        self.btn_add_connector.pack(side=TOP, anchor='w')

        # Remove

        self.fm_actions_remove = LabelFrame(self.fm_actions, text='Remove')
        self.fm_actions_remove.pack(side=TOP, anchor='w', fill=X)

        self.label_remove = Label(self.fm_actions_remove, text="Variable to remove")
        self.label_remove.pack(side=TOP, anchor='w')

        self.variable_to_remove_combobox = ttk.Combobox(self.fm_actions_remove)
        self.variable_to_remove_combobox["values"] = self.variables_in_model
        self.variable_to_remove_combobox.current(0)
        # self.variable_to_remove_combobox.bind("<<ComboboxSelected>>", self)
        self.variable_to_remove_combobox.pack(side=TOP)

        self.btn_remove = Button(self.fm_actions_remove, text='Remove', command=self.remove_element)
        self.btn_remove.pack(side=TOP, anchor='w')

        # Modify

        self.fm_actions_modify = LabelFrame(self.fm_actions, text='Modify')
        self.fm_actions_modify.pack(side=TOP, anchor='w', fill=X)

        self.label_modify = Label(self.fm_actions_modify, text="Variable to modify")
        self.label_modify.pack(side=TOP, anchor='w')

        self.variable_to_modify_combobox = ttk.Combobox(self.fm_actions_modify)
        self.variable_to_modify_combobox["values"] = self.variables_in_model
        self.variable_to_modify_combobox.current(0)
        self.variable_to_modify_combobox.bind("<<ComboboxSelected>>", self.on_select_var_to_modify)
        self.variable_to_modify_combobox.pack(side=TOP, anchor='w')

        self.label_equation = Label(self.fm_actions_modify, text="Equation")
        self.label_equation.pack(side=TOP, anchor='w')
        self.entry_equation = Entry(self.fm_actions_modify)
        self.entry_equation.pack(side=TOP)

        self.label_x = Label(self.fm_actions_modify, text="X position")
        self.label_x.pack(side=TOP, anchor='w')
        self.entry_x = Entry(self.fm_actions_modify)
        self.entry_x.pack(side=TOP)

        self.label_y = Label(self.fm_actions_modify, text="Y position")
        self.label_y.pack(side=TOP, anchor='w')
        self.entry_y = Entry(self.fm_actions_modify)
        self.entry_y.pack(side=TOP)

        self.btn_modify = Button(self.fm_actions_modify, text='Modify', command=self.modify_element)
        self.btn_modify.pack(side=TOP, anchor='w')

        # End of Actions

        self.stock_and_flow_diagram = SFDCanvas(self)
        self.stock_and_flow_diagram.pack(side=LEFT, fill=BOTH)

        self.fm_display_cld = Frame(self)
        self.fm_display_cld.pack(side=LEFT, fill=BOTH)

        self.refresh_display_structure()

    def refresh_display_structure(self):
        # Controller
        self.variables_in_model = list(self.structure.model_structure.sfd.nodes)
        self.variable_to_remove_combobox["values"] = self.variables_in_model
        self.variable_to_modify_combobox["values"] = self.variables_in_model

        # CLD

        try:
            plt.close()
            self.candidate_structure_canvas.get_tk_widget().destroy()
        except:
            pass
        fig, ax = plt.subplots()

        node_attrs_function = nx.get_node_attributes(self.structure.model_structure.sfd, 'function')
        node_attrs_value = nx.get_node_attributes(self.structure.model_structure.sfd, 'value')
        custom_node_labels = dict()
        for node, attr in node_attrs_function.items():
            # when the element only has a value but no function
            if attr is None:
                attr = node_attrs_value[node][0]
            # when the element has a function
            else:
                attr = equation_to_text(attr)
            custom_node_labels[node] = "{}={}".format(node, attr)

        edge_attrs_polarity = nx.get_edge_attributes(self.structure.model_structure.sfd, 'polarity')
        custom_edge_colors = list()
        for edge, attr in edge_attrs_polarity.items():
            color = 'k'  # black
            if attr == 'negative':
                color = 'b'  # blue
            custom_edge_colors.append(color)

        nx.draw_networkx(G=self.structure.model_structure.sfd,
                         labels=custom_node_labels,
                         font_size=8,
                         node_color='skyblue',
                         edge_color=custom_edge_colors)
        plt.axis('off')  # turn off axis for structure display
        self.candidate_structure_canvas = FigureCanvasTkAgg(figure=fig, master=self.fm_display_cld)
        self.candidate_structure_canvas.get_tk_widget().configure(width=500, height=400)
        self.candidate_structure_canvas.get_tk_widget().pack(side=LEFT)

        # SFD
        self.stock_and_flow_diagram.reset_canvas()
        self.stock_and_flow_diagram.draw_sfd(sfd=self.structure.model_structure.sfd)

        # Simulation
        self.structure.simulation_handler(25)

    def add_stock(self):
        add_dialog = AddElementWindow(element_type=STOCK, structure=self.structure)
        self.wait_window(add_dialog)  # important!
        self.refresh_display_structure()

    def add_flow(self):
        add_dialog = AddElementWindow(element_type=FLOW, structure=self.structure)
        self.wait_window(add_dialog)  # important!
        self.refresh_display_structure()

    def add_variable(self):
        add_dialog = AddElementWindow(element_type=VARIABLE, structure=self.structure)
        self.wait_window(add_dialog)  # important!
        self.refresh_display_structure()

    def add_connector(self):
        add_connector_dialog = AddConnectorWindow(structure=self.structure)
        self.wait_window(add_connector_dialog)
        self.refresh_display_structure()

    def remove_element(self):
        var_to_remove = self.variable_to_remove_combobox.get()
        self.structure.delete_variable(name=var_to_remove)
        self.refresh_display_structure()

    def on_select_var_to_modify(self, evt):
        print("Check,", self.structure.model_structure.sfd.nodes[self.variable_to_modify_combobox.get()])
        original_equation = self.structure.model_structure.sfd.nodes[self.variable_to_modify_combobox.get()]['function']
        if original_equation is None:
            original_equation = self.structure.model_structure.sfd.nodes[self.variable_to_modify_combobox.get()]['value'][0]
        original_equation_text = equation_to_text(original_equation)
        self.entry_equation.delete(0, END)
        self.entry_equation.insert(0, original_equation_text)

        x_pos = self.structure.model_structure.sfd.nodes[self.variable_to_modify_combobox.get()]['pos'][0]
        self.entry_x.delete(0, END)
        self.entry_x.insert(0, x_pos)

        y_pos = self.structure.model_structure.sfd.nodes[self.variable_to_modify_combobox.get()]['pos'][1]
        self.entry_y.delete(0, END)
        self.entry_y.insert(0, y_pos)

    def modify_element(self):
        new_equation = text_to_equation(self.entry_equation.get())
        # # decide if this new equation is a number or not (starting with a number)
        # if new_equation[0].isdigit():
        #     new_equation = [float(new_equation)]
        # else:
        #     new_equation = text_to_equation(equation_text=new_equation)
        #     print("new equation generated:", new_equation)
        self.structure.model_structure.replace_equation(name=self.variable_to_modify_combobox.get(),
                                                        new_equation=new_equation)

        new_x = float(self.entry_x.get())
        new_y = float(self.entry_y.get())
        self.structure.model_structure.sfd.nodes[self.variable_to_modify_combobox.get()]['pos'][0] = new_x
        self.structure.model_structure.sfd.nodes[self.variable_to_modify_combobox.get()]['pos'][1] = new_y

        self.refresh_display_structure()


class AddElementWindow(Toplevel):
    def __init__(self, element_type, structure, width=200, height=350, x=200, y=200):
        super().__init__()
        self.title("Add " + element_type)
        self.geometry("+{}+{}".format(x, y))
        self.element_type = element_type
        self.structure = structure

        self.label_name = Label(self, text="Name:")
        self.label_name.pack(side=TOP, anchor='w')
        self.entry_name = Entry(self)
        self.entry_name.pack(side=TOP)

        self.label_value = Label(self, text="Value:")
        self.label_value.pack(side=TOP, anchor='w')
        self.entry_value = Entry(self)
        self.entry_value.pack(side=TOP)

        self.label_x = Label(self, text="x:")
        self.label_x.pack(side=TOP, anchor='w')
        self.entry_x = Entry(self)
        self.entry_x.pack(side=TOP)

        self.label_y = Label(self, text="y:")
        self.label_y.pack(side=TOP, anchor='w')
        self.entry_y = Entry(self)
        self.entry_y.pack(side=TOP)

        if self.element_type == FLOW:
            self.variables_in_model = ['-'] + self.structure.model_structure.all_certain_type(STOCK)

            self.label_flow_to = Label(self, text="Flow to:")
            self.label_flow_to.pack(side=TOP, anchor='w')

            self.flow_to_variables_combobox = ttk.Combobox(self)
            self.flow_to_variables_combobox["values"] = self.variables_in_model
            self.flow_to_variables_combobox.current(0)
            self.flow_to_variables_combobox.pack(side=TOP)

            self.label_flow_from = Label(self, text="Flow from:")
            self.label_flow_from.pack(side=TOP, anchor='w')

            self.flow_from_variables_combobox = ttk.Combobox(self)
            self.flow_from_variables_combobox["values"] = self.variables_in_model
            self.flow_from_variables_combobox.current(0)
            self.flow_from_variables_combobox.pack(side=TOP)

        self.fm_buttons = Frame(self)
        self.fm_buttons.pack(side=TOP, anchor='center')
        self.confirm_button = Button(self.fm_buttons, text='Confirm', command=self.confirm)
        self.confirm_button.pack(side=LEFT, anchor='center')
        self.confirm_button = Button(self.fm_buttons, text='Cancel', command=self.cancel)
        self.confirm_button.pack(side=LEFT, anchor='center')

    def confirm(self):
        try:
            print("Manually adding element:")
            self.element_name = self.entry_name.get()
            self.value = text_to_equation(self.entry_value.get())
            self.x = int(self.entry_x.get())
            self.y = int(self.entry_y.get())
            print("name: {}, value: {}, x: {}, y:{}".format(self.element_name, self.value, self.x, self.y))
            if self.element_type == FLOW:
                self.flow_from = None if self.flow_from_variables_combobox.get() == '-' else self.flow_from_variables_combobox.get()
                self.flow_to = None if self.flow_to_variables_combobox.get() == '-' else self.flow_to_variables_combobox.get()
                # print("flow_from: {}, flow_to: {}".format(self.flow_from, self.flow_to))

            if self.element_type == STOCK:
                self.structure.build_stock(name=self.element_name, initial_value=self.value, x=self.x, y=self.y)
            elif self.element_type == FLOW:
                self.structure.build_flow(name=self.element_name, equation=self.value, x=self.x, y=self.y,
                                          flow_from=self.flow_from, flow_to=self.flow_to)
                self.structure.connect_stock_flow(flow_name=self.element_name,
                                                  new_flow_from=self.flow_from,
                                                  new_flow_to=self.flow_to)
            elif self.element_type in [VARIABLE, PARAMETER]:
                self.structure.build_aux(name=self.element_name, equation=self.value, x=self.x, y=self.y)

            # simulate this modified structure
            # self.structure.simulation_handler(25)
            self.destroy()

        except ValueError:
            pass

    def cancel(self):
        self.destroy()


class AddConnectorWindow(Toplevel):
    def __init__(self, structure, x=200, y=200):
        super().__init__()
        self.title("Add causal link")
        self.geometry("+{}+{}".format(x, y))
        self.structure = structure

        self.variables_in_model = list(self.structure.model_structure.sfd.nodes)

        self.label_from = Label(self, text="From")
        self.label_from.pack(side=TOP, anchor='w')

        self.from_variable_combobox = ttk.Combobox(self)
        self.from_variable_combobox["values"] = self.variables_in_model
        self.from_variable_combobox.current(0)
        # self.flow_from_variables_combobox.bind("<<ComboboxSelected>>", self)
        self.from_variable_combobox.pack(side=TOP)

        self.label_to = Label(self, text="To")
        self.label_to.pack(side=TOP, anchor='w')

        self.to_variable_combobox = ttk.Combobox(self)
        self.to_variable_combobox["values"] = self.variables_in_model
        self.to_variable_combobox.current(0)
        # self.flow_to_variables_combobox.bind("<<ComboboxSelected>>", self)
        self.to_variable_combobox.pack(side=TOP)

        self.label_polarity = Label(self, text="Polarity")
        self.label_polarity.pack(side=TOP, anchor='w')

        self.polarity_combobox = ttk.Combobox(self)
        self.polarity_combobox["values"] = ['-', 'positive', 'negative']
        self.polarity_combobox.current(0)
        # self.flow_to_variables_combobox.bind("<<ComboboxSelected>>", self)
        self.polarity_combobox.pack(side=TOP)

        self.fm_buttons = Frame(self)
        self.fm_buttons.pack(side=TOP, anchor='center')
        self.confirm_button = Button(self.fm_buttons, text='Confirm', command=self.confirm)
        self.confirm_button.pack(side=LEFT, anchor='center')
        self.confirm_button = Button(self.fm_buttons, text='Cancel', command=self.cancel)
        self.confirm_button.pack(side=LEFT, anchor='center')

    def confirm(self):
        try:
            from_var = self.from_variable_combobox.get()
            to_var = self.to_variable_combobox.get()
            polarity = self.polarity_combobox.get() if self.polarity_combobox.get() != '-' else None
            # print("from var: {}, to var: {}, polarity: {}".format(from_var, to_var, polarity))
            self.structure.build_connector(from_var=from_var, to_var=to_var, polarity=polarity)
            self.destroy()

        except ValueError:
            pass

    def cancel(self):
        self.destroy()


class GenericStructureManager(object):
    """The class containing and managing all generic structures"""

    def __init__(self):
        self.generic_structures = dict()  # name:structure
        self.generic_structures_likelihood = dict()  # name:likelihood
        self.add_generic_structure(name='basic_stock_inflow')
        self.add_generic_structure(name='basic_stock_outflow')
        self.add_generic_structure(name='first_order_positive')
        self.add_generic_structure(name='first_order_negative')

        self.generic_structures_likelihood_window = GenericStructuresLikelihoodWindow(
            generic_structures_likelihood=self.generic_structures_likelihood)
        self.generic_structures_likelihood_window.create_likelihood_display()

    def add_generic_structure(self, name, likelihood=INITIAL_LIKELIHOOD):
        a = SessionHandler()
        a.model_structure.set_predefined_structure[name]()
        a.model_structure.simulate(simulation_time=25)
        # a.model_structure.sfd.graph['likelihood'] = likelihood
        self.generic_structures[name] = a
        self.generic_structures_likelihood[name] = likelihood

    def reset_all_likelihood(self):
        for generic_structure in self.generic_structures_likelihood.keys():
            self.generic_structures_likelihood[generic_structure] = INITIAL_LIKELIHOOD

    def generate_distribution(self):
        """Generate a list, containing multiple uids of each structure"""
        distribution_list = list()
        for generic_structure in self.generic_structures_likelihood.keys():
            for i in range(self.generic_structures_likelihood[generic_structure]):
                distribution_list.append(generic_structure)
        return distribution_list

    def random_single(self):
        """Return one structure"""
        random_generic_structure_name = random.choice(self.generate_distribution())
        print('\n    {} is chosen as target_structure;\n'.format(random_generic_structure_name))
        return self.generic_structures[random_generic_structure_name]

    def random_pair(self):
        """Return a pair of structures for competition"""
        random_two = random.choices(self.generate_distribution(), k=2)

        return random_two

    def update_likelihood_elo(self, winner, loser):
        """Update winner and loser's activity using Elo Rating System"""
        r_winner = self.generic_structures_likelihood[winner]
        r_loser = self.generic_structures_likelihood[loser]
        e_winner = 1 / (1 + 10 ** ((r_loser - r_winner) / 400))
        e_loser = 1 / (1 + 10 ** ((r_winner - r_loser) / 400))
        gain_winner = 1
        gain_loser = 0
        k = 4  # maximum points one can gain or lose in one round
        r_winner = r_winner + k * (gain_winner - e_winner)
        r_loser = r_loser + k * (gain_loser - e_loser)

        def normalize(r):
            if r > 50:
                r = 50
            elif r < 1:
                r = 1
            return r

        self.generic_structures_likelihood[winner] = round(normalize(r_winner))
        self.generic_structures_likelihood[loser] = round(normalize(r_loser))

        self.generic_structures_likelihood_window.update_likelihood_display()


class GenericStructuresLikelihoodWindow(Toplevel):
    def __init__(self, generic_structures_likelihood=None, window_title="Generic Structures", width=250, height=90,
                 x=350, y=50):
        super().__init__()
        self.title(window_title)
        self.width = width
        self.height = height
        self.geometry("{}x{}+{}+{}".format(width, height, x, y))
        self.generic_structures_likelihood = generic_structures_likelihood

        self.fm_labels = Frame(master=self, width=self.width)
        self.fm_labels.pack(side=LEFT, anchor='nw')

        self.labels = list()

    def create_likelihood_display(self):
        for item, llikelihood in self.generic_structures_likelihood.items():
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
    root.wm_title("Expansion Panel")
    root.configure(background='#fff')
    ExpansionPanel(root)
    root.mainloop()


if __name__ == '__main__':
    main()
