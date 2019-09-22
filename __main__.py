import sys
from main_window_structure_generator import Ui_MainWindow
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from config import ITERATION_TIMES, ACTIVITY_DEMOMINATOR, INITIAL_LIKELIHOOD, INITIAL_ACTIVITY, REFERENCE_MODE_PATH, \
    COOL_DOWN_TIMES, COOL_DOWN_SWITCH, GENERIC_STRUCTURE_LIKELIHOOD_UPDATE_TIMES, PURGE_SWITCH, PURGE_THRESHOLD
from StockAndFlowInPython.session_handler import SessionHandler, NewGraphNetworkWindow
from StockAndFlowInPython.structure_utilities.structure_utilities import new_expand_structure, create_causal_link, \
    apply_a_concept_cld, optimize_parameters, import_flow
from StockAndFlowInPython.behaviour_utilities.behaviour_utilities import similarity_calc_pattern, categorize_behavior
from StockAndFlowInPython.graph_sd.graph_based_engine import STOCK, FLOW, VARIABLE, PARAMETER, CONNECTOR, ALIAS, \
    MULTIPLICATION, LINEAR, SUBTRACTION, DIVISION, ADDITION
from StockAndFlowInPython.sfd_canvas.sfd_canvas_qt import SFDCanvas
from StockAndFlowInPython.parsing.XMILE_parsing import equation_to_text, text_to_equation
import pandas as pd
import numpy as np
import networkx as nx
import networkx.algorithms.isomorphism as iso
import matplotlib.pyplot as plt
import random


class IntegratedWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(IntegratedWindow, self).__init__()
        self.setupUi(self)

        self.listWidget_time_series.itemClicked.connect(self.show_time_series)

        self.button_group_ref_type = QButtonGroup(self)
        self.button_group_ref_type.addButton(self.radioButton_stock, 1)
        self.button_group_ref_type.addButton(self.radioButton_flow, 2)
        self.button_group_ref_type.addButton(self.radioButton_aux, 3)

        self.pushButton_add_ref.clicked.connect(self.add_reference_mode_from_time_series)

        self.pushButton_remove_ref.clicked.connect(self.remove_reference_mode)

        self.listWidget_reference_modes.itemClicked.connect(self.show_reference_mode)

        self.actionStartExpansion.triggered.connect(self.expansion_loop)

        self.listWidget_candidates.itemClicked.connect(self.display_a_candidate_structure_sfd)
        self.listWidget_candidates.itemClicked.connect(self.display_a_candidate_structure_cld)
        self.listWidget_candidates.itemClicked.connect(self.display_a_candidate_structure_behavior)

        self.pushButton_accept_candidate_structure.clicked.connect(self.accept_a_candidate_structure)
        self.pushButton_remove_candidate_structure.clicked.connect(self.remove_a_candidate_structure)
        self.pushButton_modify_candidate_structure.clicked.connect(self.modify_a_candidate_structure)

        self.pushButton_add_binding.clicked.connect(self.add_binding)
        self.pushButton_remove_binding.clicked.connect(self.remove_binding)

        self.pushButton_apply.clicked.connect(self.set_iteration_time)  # TODO move all 'settings' to one place

        self.comboBox_elements.currentIndexChanged.connect(self.display_an_element_behavior)


        # Specify round to iterate

        self.iteration_time = ITERATION_TIMES
        self.lineEdit_iteration.setText(str(self.iteration_time))

        # Initialize concept CLDs
        self.initialize_concept_CLDs()

        # Initialize time series
        self.load_time_series_from_file()

        # Initialize reference modes
        self.initialize_reference_modes()

        # Initialize generic structures
        self.initialize_generic_structures()

        # Initial expansion tree
        self.expansion_tree = nx.DiGraph()

        # Initialize candidate structures
        self.initialize_candidate_structures()

        # Initialize bindings
        self.initialize_bindings()

        # TODO this task list will be the predecessor of 'Code Rack'
        # Initialize task list
        self.task_list = [5, 4]

        # TODO test
        # self.load_reference_mode_from_file()

        # Add a root structure
        initial_structure = SessionHandler()
        self.add_structure(structure=initial_structure)

        # Reset generic structure's likelihood
        self.reset_all_generic_structures_likelihood()

        # Reset
        self.generate_generic_structures_distribution()




    def set_iteration_time(self):
        self.iteration_time = int(self.lineEdit_iteration.text())
        print("Set iteration time to {}".format(self.iteration_time))

    # TODO this is the basis for one agent's routine in the future
    def expansion_loop(self):
        i = 1
        while i <= self.iteration_time:

            if i == 1:
                self.build_element_for_reference_modes()

            print('\n\nExpansion: Iterating {}'.format(i))
            print('\nTask list: {}\n'.format(self.task_list))
            self.statusbar.showMessage('Iter ' + str(i), 3000)
            # self.lb_iteration_round.configure(text='Iter ' + str(i))
            # self.lb_iteration_round.update()

            # STEP: adjust generic structures' likelihood
            for j in range(GENERIC_STRUCTURE_LIKELIHOOD_UPDATE_TIMES):
                self.update_generic_structures_likelihood()

            # STEP: structural modification
            chosen_task = random.choice(self.task_list)
            if chosen_task == 1:
                """Generate a new candidate structure"""
                base = self.random_one_candidate_structure()
                target = self.random_one_generic_structure()
                # get all elements in base structure
                base_structure_elements = list(base.model_structure.sfd.nodes)
                # pick an element from base_structure to start with. Now: randomly. Future: guided by activity.
                start_with_element_base = random.choice(base_structure_elements)
                new = new_expand_structure(base_structure=base,
                                           start_with_element_base=start_with_element_base,
                                           target_structure=target)
                # new = expand_structure(base_structure=base, target_structure=target)
                self.derive_new_candidate_structure(base_structure=base, new_structure=new)
                # self.task_list.append(random.choice([1, 2]))
                self.task_list.append(4)

            elif chosen_task == 2:
                """Create a new causal link in an existing candidate structure"""
                base = self.random_one_candidate_structure()
                new = create_causal_link(base_structure=base)
                self.derive_new_candidate_structure(base_structure=base, new_structure=new)
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
                print("    We choose {}, uid {} as the beginning stock".format(chosen_stock_ref_name,
                                                                               chosen_stock_uid))
                pattern_name = self.categorize(behavior=self.reference_modes[chosen_stock_ref_name][1])

                # fetch concept CLD based on pattern
                concept_cld = self.get_concept_cld_by_name(concept_cld_name=pattern_name)
                print(concept_cld.nodes(data=True))

                base = self.random_one_candidate_structure()
                # TODO: this is not purely random
                target = self.random_one_generic_structure()
                new = apply_a_concept_cld(base_structure=base,
                                          stock_uid_in_base_to_start_with=chosen_stock_uid,
                                          concept_cld=concept_cld,
                                          target_structure=target)
                self.derive_new_candidate_structure(base_structure=base, new_structure=new)
                # self.task_list.append(4)

            elif chosen_task == 4:
                """Optimize parameters in a candidate structure"""
                base = self.random_one_candidate_structure()

                new = optimize_parameters(base_structure=base,
                                          reference_modes=self.reference_modes,
                                          reference_mode_bindings=self.reference_mode_bindings)
                self.derive_new_candidate_structure(base_structure=base, new_structure=new, overwrite=False)
                # self.task_list.append(5)

            elif chosen_task == 5:
                """Import a flow"""
                base = self.random_one_candidate_structure()
                target = self.random_one_generic_structure()
                # get all elements in base structure
                base_structure_stocks = list(base.model_structure.all_certain_type(STOCK))
                # pick a stock from base_structure to start with. Now: randomly. Future: guided by activity.
                start_with_element_base = random.choice(base_structure_stocks)
                new = import_flow(base_structure=base,
                                  start_with_element_base=start_with_element_base,
                                  target_structure=target)
                self.derive_new_candidate_structure(base_structure=base, new_structure=new)
                # self.task_list.append(4)

            # STEP: adjust candidate structures' activity
            self.update_candidate_structure_activity_by_behavior()

            # STEP: cool down those not simulatable structures
            if COOL_DOWN_SWITCH:
                for k in range(COOL_DOWN_TIMES):
                    self.cool_down_candidate_structures()

            # STEP: purge low activity structures
            if PURGE_SWITCH:
                self.purge_low_activity_candidate_structures()

            # STEP: sort candidate structures by activity
            # TODO: control this not only by number
            if i > 3:  # get enough candidate structures to sort
                self.sort_candidate_structures_by_activity()

            # global display updates needed
            self.refresh_candidate_structure_list()
            self.refresh_binding_list()
            # self.binding_manager.update_combobox()  # TODO: what is this?
            print('\nTask list: {}\n'.format(self.task_list))
            i += 1

    def update_candidate_structure_activity_by_behavior(self):
        if len(list(self.tree.nodes)) > 3:  # when there are more than 2 simulable candidates
            # Make more comparisons as there are more candidate structures
            iter_times = len(list(self.tree.nodes)) // 3
            for i in range(iter_times):
                # Get 2 random candidates
                random_two_candidates = [None, None]
                while random_two_candidates[0] == random_two_candidates[1]:
                    # Here we don't use the weighted random pair, to give those less active more opportunity
                    random_two_candidates = self.random_two_candidate_structures_even()
                    # while not (self.structure_manager.if_can_simulate[random_two_candidates[0]] and
                    #            self.structure_manager.if_can_simulate[random_two_candidates[1]]):
                    #     # we have to get two simulatable structures to compare their behaviors
                    #     random_two_candidates = self.structure_manager.random_pair_even()
                print("    Two candidate structures chosen for comparison: ", random_two_candidates)
                # Calculate their similarity to reference mode
                candidate_0_distance = 0
                candidate_1_distance = 0
                s_uid_0 = random_two_candidates[0]
                s_uid_1 = random_two_candidates[1]
                for reference_mode_name, reference_mode_property in self.reference_modes.items():
                    uid = self.reference_mode_bindings[reference_mode_name]
                    candidate_0_distance += self.behavioral_distance(
                        self.tree.nodes[s_uid_0]['structure'].model_structure.get_element_by_uid(uid)[
                            'value'],
                        reference_mode_property[1]
                    )
                    candidate_1_distance += self.behavioral_distance(
                        self.tree.nodes[s_uid_1]['structure'].model_structure.get_element_by_uid(uid)[
                            'value'],
                        reference_mode_property[1]
                    )

                print(candidate_0_distance, candidate_1_distance)
                # Update their activity
                if candidate_0_distance != candidate_1_distance:
                    if candidate_0_distance > candidate_1_distance:
                        self.update_candidate_structures_activity_elo(s_uid_1, s_uid_0)
                    else:
                        self.update_candidate_structures_activity_elo(s_uid_0, s_uid_1)
                # print("All nodes' activity:", self.show_all_candidate_structures_activity())

    def update_generic_structures_likelihood(self):
        random_two_generic_structures = [None, None]
        while random_two_generic_structures[0] == random_two_generic_structures[1]:  # The two cannot be the same
            random_two_generic_structures = self.random_two_generic_structures()
        generic_structure_0 = random_two_generic_structures[0]
        generic_structure_1 = random_two_generic_structures[1]
        # print(random_two_generic_structures)
        # TODO this part is important: assessment of a generic structure's likelihood.

        # randomly choose a reference mode
        chosen_reference_mode = random.choice(list(self.reference_modes.keys()))
        chosen_reference_mode_type = self.reference_modes[chosen_reference_mode][0]

        # randomly choose element from generic_structures
        chosen_element_from_generic_structure_0 = random.choice(
            self.generic_structures[generic_structure_0].model_structure.all_certain_type(
                chosen_reference_mode_type))
        chosen_element_from_generic_structure_1 = random.choice(
            self.generic_structures[generic_structure_1].model_structure.all_certain_type(
                chosen_reference_mode_type))

        random_two_generic_structures_distance = {
            generic_structure_0: self.behavioral_distance(
                self.generic_structures[generic_structure_0].model_structure.sfd.node[
                    chosen_element_from_generic_structure_0]['value'],
                self.reference_modes[chosen_reference_mode][1]),
            generic_structure_1: self.behavioral_distance(
                self.generic_structures[generic_structure_1].model_structure.sfd.node[
                    chosen_element_from_generic_structure_1]['value'],
                self.reference_modes[chosen_reference_mode][1])
        }
        # print(random_two_generic_structures_distance)
        # a larger distance -> a lower likelihood
        if random_two_generic_structures_distance[random_two_generic_structures[0]] < \
                random_two_generic_structures_distance[random_two_generic_structures[1]]:
            self.update_generic_structures_likelihood_elo(random_two_generic_structures[0],
                                                          random_two_generic_structures[1])
        else:
            self.update_generic_structures_likelihood_elo(random_two_generic_structures[1],
                                                          random_two_generic_structures[0])
        print(self.generic_structures_likelihood)

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





    def initialize_concept_CLDs(self):
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




    def load_time_series_from_file(self):
        """
        The logic is: file -> file in memory (numerical data) -> time series --selection--> reference mode
        :return:
        """
        self.reference_mode_path = REFERENCE_MODE_PATH
        self.numerical_data = None
        self.time_series = dict()

        if self.reference_mode_path is None and len(self.time_series) == 0:  # either path not specified and no t-series
            self.get_reference_mode_file_name()
        self.numerical_data = pd.read_csv(self.reference_mode_path)
        for column in self.numerical_data:
            self.time_series[column] = self.numerical_data[column].tolist()
        self.listWidget_time_series.addItems(self.time_series)

    def show_time_series(self):
        selected_time_series_name = self.listWidget_time_series.currentItem().text()
        selected_time_series = self.time_series[selected_time_series_name]

        self.clear_detail_panel()
        self.put_time_series_to_detail_panel(time_series=selected_time_series,
                                             time_series_name=selected_time_series_name)

    def add_reference_mode_from_time_series(self):
        reference_mode_type = None
        if self.button_group_ref_type.checkedId() != -1:
            if self.button_group_ref_type.checkedId() == 1:
                reference_mode_type = STOCK
            elif self.button_group_ref_type.checkedId() == 2:
                reference_mode_type = FLOW
            elif self.button_group_ref_type.checkedId() == 3:
                reference_mode_type = VARIABLE  # TODO: Parameter?
            print(reference_mode_type)
        else:
            print("Reference mode type is not indicated. Please indicate one.")

        selected_time_series_name = self.listWidget_time_series.currentItem().text()
        selected_time_series = self.time_series[selected_time_series_name]
        if reference_mode_type is not None and selected_time_series is not None:
            self.reference_modes[selected_time_series_name] = [reference_mode_type, selected_time_series]
            print("Added reference mode for {} : {}".format(reference_mode_type, selected_time_series_name))

            # Sync UI with ref_mode_list
            self.refresh_reference_mode_list()

    def build_element_for_reference_modes(self):
        # Get the first (also only) structure from expansion tree
        structure = self.tree.nodes[list(self.tree.nodes)[0]]['structure']
        for reference_mode_name, reference_mode_properties in self.reference_modes.items():
            print("AAAA", reference_mode_name, reference_mode_properties)
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
                # self.binding_manager.generate_binding_list_box()  # TODO: What is this?
        structure.simulation_handler(25)




    def initialize_reference_modes(self):
        # Reference modes
        self.reference_modes = dict()  # name : [type, time_series]

    def refresh_reference_mode_list(self):
        # Sync UI with ref_mode_list
        all_ref_mode_names_in_list = [str(self.listWidget_reference_modes.item(i).text()) \
                                    for i in range(self.listWidget_reference_modes.count())]
        for ref_mode_name in list(self.reference_modes.keys()):
            if ref_mode_name not in all_ref_mode_names_in_list:
                self.listWidget_reference_modes.addItem(ref_mode_name)

    def remove_reference_mode(self):
        selected_reference_mode = self.listWidget_reference_modes.currentItem().text()
        self.reference_modes.pop(selected_reference_mode)
        self.listWidget_reference_modes.takeItem(self.listWidget_reference_modes.row(self.listWidget_reference_modes.findItems(selected_reference_mode,
                                                                                           Qt.MatchExactly)[0]))
        # logic: text matches item --> get the row of this item --> take item from the listWidget by row
        # could done in another way: just re-generate all items in the list widget over again once any change is made

    def show_reference_mode(self):
        selected_reference_mode_name = self.listWidget_reference_modes.currentItem().text()
        selected_reference_mode_type = self.reference_modes[selected_reference_mode_name][0]
        selected_reference_mode_time_series = self.reference_modes[selected_reference_mode_name][1]

        self.clear_detail_panel()
        self.put_time_series_to_detail_panel(time_series=selected_reference_mode_time_series,
                                             time_series_name=selected_reference_mode_name)

        self.label_detail_ref_mode_type = QLabel('Type: '+selected_reference_mode_type)
        self.label_detail_ref_mode_type.setAlignment(Qt.AlignHCenter)
        self.layout_details.addWidget(self.label_detail_ref_mode_type)





    def clear_detail_panel(self):
        for i in reversed(range(self.layout_details.count())):
            self.layout_details.itemAt(i).widget().setParent(None)

    def put_time_series_to_detail_panel(self, time_series, time_series_name):
        self.layout_details.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.details_behavior_canvas = self.time_series_to_widget(time_series=time_series,
                                                                  label=time_series_name)
        self.details_behavior_canvas.setFixedSize(400, 320)
        self.layout_details.addWidget(self.details_behavior_canvas)

    def clear_result_panel(self):
        for i in reversed(range(self.layout_show_behavior.count())):
            self.layout_show_behavior.itemAt(i).widget().setParent(None)

    def put_time_series_to_result_panel(self, time_series, time_series_name):
        self.layout_show_behavior.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.result_behavior_canvas = self.time_series_to_widget(time_series=time_series,
                                                                 label=time_series_name)
        self.result_behavior_canvas.setFixedSize(400, 320)
        self.layout_show_behavior.addWidget(self.result_behavior_canvas)





    def initialize_generic_structures(self):
        self.generic_structures = dict()  # name:structure
        self.generic_structures_likelihood = dict()  # name:likelihood
        self.add_generic_structure(name='basic_stock_inflow')
        self.add_generic_structure(name='basic_stock_outflow')
        # self.add_generic_structure(name='first_order_positive')
        # self.add_generic_structure(name='first_order_negative')

    def add_generic_structure(self, name, likelihood=INITIAL_LIKELIHOOD):
        a = SessionHandler()
        a.model_structure.set_predefined_structure[name]()
        a.model_structure.simulate(simulation_time=25)
        # a.model_structure.sfd.graph['likelihood'] = likelihood
        self.generic_structures[name] = a
        self.generic_structures_likelihood[name] = likelihood

    def reset_all_generic_structures_likelihood(self):
        for generic_structure in self.generic_structures_likelihood.keys():
            self.generic_structures_likelihood[generic_structure] = INITIAL_LIKELIHOOD

    def generate_generic_structures_distribution(self):
        """Generate a list, containing multiple uids of each structure"""
        distribution_list = list()
        for generic_structure in self.generic_structures_likelihood.keys():
            for i in range(self.generic_structures_likelihood[generic_structure]):
                distribution_list.append(generic_structure)
        return distribution_list

    def random_one_generic_structure(self):
        """Return one structure"""
        random_generic_structure_name = random.choice(self.generate_generic_structures_distribution())
        print('\n    {} is chosen as target_structure;\n'.format(random_generic_structure_name))
        return self.generic_structures[random_generic_structure_name]

    def random_two_generic_structures(self):
        """Return a pair of structures for competition"""
        random_two = random.choices(self.generate_generic_structures_distribution(), k=2)

        return random_two

    def update_generic_structures_likelihood_elo(self, winner, loser):
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

        self.refresh_generic_structures_list()

    def refresh_generic_structures_list(self):
        pass







    def initialize_candidate_structures(self):
        self.tree = nx.DiGraph()
        self.candidate_structure_uid = 0
        self.sorted_tree = list()
        self.those_cannot_simulate = list()

    def sort_candidate_structures_by_activity(self):
        # sort all candidate structures by activity
        self.sorted_tree = sorted(list(self.tree.nodes(data='activity')), key=lambda x: x[1], reverse=True)
        print('Sorted tree:', self.sorted_tree)
        string = ''
        for i in range(3):
            string += str(self.sorted_tree[i][0]) + '[{}] '.format(self.sorted_tree[i][1])
        self.candidate_structure_window.label_top_three_0.configure(text=string)
        self.candidate_structure_window.label_top_three_0.update()

    def show_all_candidate_structures_activity(self):
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

    def get_uid_by_candidate_structure(self, structure):
        # print(self.tree.nodes(data=True))
        for u in list(self.tree.nodes):
            if self.tree.nodes[u]['structure'] == structure:
                return u
        print(
            '    StructureManager: Can not find uid for given structure {}.'.format(structure))

    def derive_new_candidate_structure(self, base_structure, new_structure, overwrite=False):
        """Derive a new structure from an existing one"""
        # # this is designed for 'optimization of parameters', cuz
        if overwrite:
            base_uid = self.get_uid_by_structure(structure=base_structure)
            self.tree.nodes[base_uid]['structure'] = new_structure
            base_structure.simulation_handler(25)
            return

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
            self.tree.nodes[self.get_uid_by_candidate_structure(base_structure)]['activity'] += 1
            print("    The new structure is identical to the base structure")
            return
        # 2. identical to a neighbor of the base_structure
        for neighbour in self.tree.neighbors(self.get_uid_by_candidate_structure(base_structure)):
            GM = iso.DiGraphMatcher(self.tree.nodes[neighbour]['structure'].model_structure.sfd,
                                    new_structure.model_structure.sfd,
                                    node_match=iso.categorical_node_match(
                                        attr=['function', 'flow_from', 'flow_to', 'value'],
                                        # attr=['equation', 'value'],
                                        default=[None, None, None, None],
                                        # default=[None, None]
                                        )
                                    )
            if GM.is_isomorphic():
                # if nx.is_isomorphic(self.tree.nodes[neighbour]['structure'].model_structure.sfd, new_structure.model_structure.sfd):
                self.tree.nodes[neighbour]['activity'] += 1
                if self.tree.nodes[self.get_uid_by_candidate_structure(base_structure)]['activity'] > 1:
                    self.tree.nodes[self.get_uid_by_candidate_structure(base_structure)]['activity'] -= 1
                # print(self.tree.nodes[neighbour]['structure'].model_structure.sfd.nodes(data=True))
                # print(new_structure.model_structure.sfd.nodes(data=True))
                print("    The new structure already exists in base structure's neighbours")
                return

        # confirm a new node
        new_uid = self.get_new_candidate_structure_uid()
        print('    Deriving structure from {} to {}'.format(self.get_uid_by_candidate_structure(base_structure), new_uid))
        # TODO: Activity dynamics
        # 1. A newly derived structure should gain focus for a while
        # 2. If it is not promising enough, its newly gained activity will be transferred to other candidates through comparison
        # new_activity = self.tree.nodes[self.get_uid_by_structure(base_structure)]['activity'] // ACTIVITY_DEMOMINATOR
        new_activity = 40
        self.tree.add_node(new_uid,
                           structure=new_structure,
                           activity=new_activity
                           )

        # subtraction this part of activity from the base_structure
        # self.tree.nodes[self.get_uid_by_structure(base_structure)]['activity'] -= new_activity
        # if self.tree.nodes[self.get_uid_by_structure(base_structure)]['activity'] < 1:
        #     self.tree.nodes[self.get_uid_by_structure(base_structure)]['activity'] = 1

        # build a link from the old structure to the new structure
        self.tree.add_edge(self.get_uid_by_candidate_structure(base_structure), new_uid)
        # simulate this new structure

        new_structure.simulation_handler(25)

        # TODO: decide if this part still needs to be kept, for all candidate structures are supposed to be simulatable.
        # try:
        #     new_structure.simulation_handler(25)
        #     self.if_can_simulate[new_uid] = True
        #     self.those_can_simulate.append(new_uid)
        # except KeyError:
        #     self.if_can_simulate[new_uid] = False
        #     self.those_cannot_simulate.append(new_uid)
        #
        # print("Simulatable structures:", self.if_can_simulate)

        # self.update_candidate_structure_window()  # TODO: What is this?

        # highlight the newly derived structure #Todo: why this is not working?
        # self.candidate_structure_window.candidate_structure_list_box.activate(new_uid)

    def cool_down_candidate_structures(self):
        """Cool down structures"""
        for u in self.tree.nodes:  # no matter it is simulatable or not
            # for u in self.those_cannot_simulate:
            self.tree.nodes[u]['activity'] = self.tree.nodes[u]['activity'] - 1 if self.tree.nodes[u][
                                                                                       'activity'] > 1 else 1
        self.refresh_candidate_structure_list()

    def random_one_candidate_structure(self):
        """Return one structure"""
        random_structure_uid = random.choice(self.generate_candidate_structures_distribution_weighted())
        print('\n    No.{} is chosen as base_structure;\n'.format(random_structure_uid))
        return self.tree.nodes[random_structure_uid]['structure']

    def random_two_candidate_structures_weighted(self):
        """Return a pair of structures for competition"""
        random_structures_uid = random.choices(self.generate_candidate_structures_distribution_weighted(), k=2)
        return random_structures_uid

    def random_two_candidate_structures_even(self):
        random_structures_uid = random.choices(list(self.tree.nodes), k=2)
        return random_structures_uid

    def update_candidate_structures_activity_elo(self, winner, loser):
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

    def generate_candidate_structures_distribution_weighted(self):
        """Generate a list, containing multiple uids of each structure with weighted distribution"""
        distribution_list = list()
        for u in list(self.tree.nodes):
            for i in range(self.tree.nodes[u]['activity']):
                distribution_list.append(u)
        return distribution_list

    def purge_low_activity_candidate_structures(self):
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

    def accept_a_candidate_structure(self):
        # get the selected structure (entry) from list
        selected_candidate_structure = int(self.listWidget_candidates.currentItem().text())

        # remove all other nodes from the tree
        elements = list(self.tree.nodes)
        elements.remove(selected_candidate_structure)
        self.tree.remove_nodes_from(elements)

        # regenerate list box
        self.refresh_candidate_structure_list()

        # TODO: update tree display

    def modify_a_candidate_structure(self):
        if self.listWidget_candidates.currentItem() is not None:
            pass
        # TODO: Structure modifier should be built elsewhere and imported as a widget

    def remove_a_candidate_structure(self):
        selected_candidate_structure = int(self.listWidget_candidates.currentItem().text())
        self.tree.remove_node(selected_candidate_structure)  # int as node, str as item in Listwidget
        self.listWidget_candidates.takeItem(self.listWidget_candidates.row(
            self.listWidget_candidates.findItems(
                str(selected_candidate_structure), Qt.MatchExactly
            )[0]
        ))

    def refresh_candidate_structure_list(self):
        all_candidate_structure_names_in_list = [str(self.listWidget_candidates.item(i).text()) \
                                                 for i in range(self.listWidget_candidates.count())]
        # one way
        for candidate_structure_name in list(self.tree.nodes):
            if str(candidate_structure_name) not in all_candidate_structure_names_in_list:
                self.listWidget_candidates.addItem(str(candidate_structure_name))
        # the other way around
        for candidate_structure_name_in_list in all_candidate_structure_names_in_list:
            if int(candidate_structure_name_in_list) not in list(self.tree.nodes):
                self.listWidget_candidates.takeItem(self.listWidget_candidates.row(
                    self.listWidget_candidates.findItems(
                        candidate_structure_name_in_list, Qt.MatchExactly
                    )[0]
                ))

    def display_a_candidate_structure_sfd(self):
        pass

    def display_a_candidate_structure_cld(self):
        pass

    def display_a_candidate_structure_behavior(self):
        self.selected_candidate_structure = int(self.listWidget_candidates.currentItem().text())
        # clear combobox
        self.comboBox_elements.clear()

        # insert element names into combobox
        self.comboBox_elements.addItems(list(self.tree.nodes[self.selected_candidate_structure]['structure'].model_structure.sfd.nodes))

    def display_an_element_behavior(self):
        # clear result panel
        self.clear_result_panel()
        selected_element_of_structure = self.comboBox_elements.currentText()
        if selected_element_of_structure != '':
            print("{} is selected for displaying behavior".format(selected_element_of_structure))

            self.put_time_series_to_result_panel(time_series=self.tree.nodes[self.selected_candidate_structure]['structure'].model_structure.sfd.nodes[selected_element_of_structure]['value'],
                                                 time_series_name=selected_element_of_structure)
        else:
            print("No element has been selected")




    def initialize_bindings(self):
        self.reference_mode_bindings = dict()  # reference_mode_name : uid of element

    def display_a_binding(self):
        pass

    def add_binding(self):
        pass

    def remove_binding(self):
        pass

    def get_binding_element_name_by_ref_name(self):
        pass

    def select_candidate_structure(self):
        pass

    def select_variable(self):
        pass

    def select_reference_mode(self):
        pass

    def generate_binding_list_box(self):
        pass

    def show_binding_details(self):
        pass

    def update_combobox(self):
        pass

    def refresh_binding_list(self):
        pass

    def time_series_to_widget(self, time_series, label):
        # plt.cla()
        fig = plt.figure(dpi=70)
        # ax = self.fig.add_axes([0.1, 0.1, 0.8, 0.8])
        ax = fig.add_subplot(111)
        # ax.set_xlim([-1, 6])
        # ax.set_ylim([-1, 6])
        ax.plot(time_series, '*')
        ax.set_xlabel("Time")
        ax.set_ylabel(label)
        canvas = FigureCanvasQTAgg(fig)
        return canvas


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = IntegratedWindow()
    win.show()
    sys.exit(app.exec_())
