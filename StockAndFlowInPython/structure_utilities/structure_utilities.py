import networkx as nx
import copy
import random
from networkx.algorithms import chain_decomposition
from StockAndFlowInPython.graph_sd.graph_based_engine import Structure, STOCK, FLOW, VARIABLE, PARAMETER, ADDITION, SUBTRACT, MULTIPLICATION, DIVISION, LINEAR
from StockAndFlowInPython.session_handler import SessionHandler


"""
def expand_structure(base_structure, target_structure):
    # new_base = copy.deepcopy(base_structure)
    new_structure = Structure(sfd=copy.deepcopy(base_structure.model_structure.sfd),
                              uid_manager=copy.deepcopy(base_structure.model_structure.uid_manager),
                              name_manager=copy.deepcopy(base_structure.model_structure.name_manager),
                              uid_element_name=copy.deepcopy(base_structure.model_structure.uid_element_name))
    new_base = SessionHandler(model_structure=new_structure)
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
    print("    Subgraph from target_structure:{} ".format(subgraph_from_target.nodes(data='function')))

    new_base.model_structure.sfd = nx.compose(new_base.model_structure.sfd, subgraph_from_target)

    # check and fix dependencies
    # print(chosen_in_edge_in_target[1])
    in_edges_to_new_node = target_structure.model_structure.sfd.in_edges(chosen_in_edge_in_target[1])
    # print(in_edges_to_new_node)
    for in_edge in in_edges_to_new_node:
        if in_edge[0] in new_base.model_structure.sfd.nodes and in_edge not in new_base.model_structure.sfd.edges:
            print("Found a missing edge: ", in_edge)
            new_base.model_structure.sfd.add_edge(*in_edge)

    print("New structure nodes:", new_base.model_structure.sfd.nodes.data('function'))
    print("New structure edges:", new_base.model_structure.sfd.edges.data())

    return new_base
"""


def new_expand_structure(base_structure, target_structure):
    # new_base = copy.deepcopy(base_structure)
    # print("    Base_structure: ", new_base.model_structure.sfd.nodes(data='function', default='Not available'))
    # new_base = copy.deepcopy(base_structure)
    new_model_structure = Structure(sfd=copy.deepcopy(base_structure.model_structure.sfd),
                                    uid_manager=copy.deepcopy(base_structure.model_structure.uid_manager),
                                    name_manager=copy.deepcopy(base_structure.model_structure.name_manager),
                                    uid_element_name=copy.deepcopy(base_structure.model_structure.uid_element_name))
    new_base = SessionHandler(model_structure=new_model_structure)
    print("    Base_structure: ", new_base.model_structure.sfd.nodes(data='function'))

    # get all elements in base structure
    base_structure_elements = list(new_base.model_structure.sfd.nodes)
    # pick an element from base_structure to start with. Now: randomly. Future: guided by activity.
    start_with_element_base = random.choice(base_structure_elements)
    print("    **** {} in base structure is chosen to start with".format(start_with_element_base))
    # print("    **** Details: ", new_base.model_structure.sfd.nodes[start_with_element_base])

    def import_flow_from_target():
        all_flows_in_target = target_structure.model_structure.all_certain_type(FLOW)
        chosen_flow_name_in_target = random.choice(all_flows_in_target)
        print("    **** {} in target_structure is chosen to start with".format(chosen_flow_name_in_target))
        chosen_flow_in_target = target_structure.model_structure.sfd.nodes[chosen_flow_name_in_target]
        # print("    **** Details: ", chosen_flow_in_target)

        x = chosen_flow_in_target['pos'][0]
        y = chosen_flow_in_target['pos'][1]

        if chosen_flow_in_target['function'] is None:  # the chosen flow is a constant one
            equation = chosen_flow_in_target['value'][0]
        else:  # it has an equation
            # set this equation to 0: we don't put equation directly in flow. Instead, we build this equation elsewhere,
            # then replace flow by it (or 'linear' flow from it).
            equation = 0

        flow_from = None
        flow_to = None
        if chosen_flow_in_target['flow_from'] is None and chosen_flow_in_target['flow_to'] is not None:
            flow_from = None
            flow_to = start_with_element_base
        elif chosen_flow_in_target['flow_from'] is not None and chosen_flow_in_target['flow_to'] is None:
            flow_from = start_with_element_base
            flow_to = None
        # TODO there is a third possibility: the chosen flow in target structure connects 2 stocks. Leave for later.
        new_base.build_flow(equation=equation, x=x, y=y, flow_from=flow_from, flow_to=flow_to)

    def import_flow_var_param_from_target():
        chosen_var_name_in_target = random.choice(
            target_structure.model_structure.all_certain_type([FLOW, VARIABLE, PARAMETER]))
        print("    **** {} in target_structure is chosen to start with".format(chosen_var_name_in_target))
        chosen_var_in_target = target_structure.model_structure.sfd.nodes[chosen_var_name_in_target]
        # print("    **** Details: ", chosen_var_in_target)

        x = chosen_var_in_target['pos'][0]
        y = chosen_var_in_target['pos'][1]

        if chosen_var_in_target['function'] is None:  # the chosen var is a constant => Parameter
            equation = chosen_var_in_target['value'][0]
        else:  # it has a function as equation
            # Not just copy-paste the equation; but to modify its parameters to constants

            equation = copy.deepcopy(chosen_var_in_target['function'])

            if equation[0] == ADDITION:
                equation[1] = start_with_element_base
                equation[2] = 0
                uid = new_base.build_aux(equation=equation, x=x, y=y)
                element_name = new_base.model_structure.get_element_name_by_uid(uid)
                new_base.build_connector(from_var=start_with_element_base, to_var=element_name, polarity='positive')
            elif equation[0] == SUBTRACT:
                equation[1] = start_with_element_base
                equation[2] = 0
                uid = new_base.build_aux(equation=equation, x=x, y=y)
                element_name = new_base.model_structure.get_element_name_by_uid(uid)
                new_base.build_connector(from_var=start_with_element_base, to_var=element_name, polarity='positive')
            elif equation[0] == MULTIPLICATION:
                equation[1] = start_with_element_base
                equation[2] = 1
                uid = new_base.build_aux(equation=equation, x=x, y=y)
                element_name = new_base.model_structure.get_element_name_by_uid(uid)
                new_base.build_connector(from_var=start_with_element_base, to_var=element_name, polarity='positive')
            elif equation[0] == DIVISION:
                equation[1] = start_with_element_base
                equation[2] = 1
                uid = new_base.build_aux(equation=equation, x=x, y=y)
                element_name = new_base.model_structure.get_element_name_by_uid(uid)
                new_base.build_connector(from_var=start_with_element_base, to_var=element_name, polarity='positive')
            elif equation[0] == LINEAR:
                equation[1] = start_with_element_base
                uid = new_base.build_aux(equation=equation, x=x, y=y)
                element_name = new_base.model_structure.get_element_name_by_uid(uid)
                new_base.build_connector(from_var=start_with_element_base, to_var=element_name, polarity='positive')

        print("    Equation for this new var:", equation)

    # TODO this mechanism need to be changed
    start_with_element_base_type = new_base.model_structure.sfd.nodes[start_with_element_base]['element_type']
    if start_with_element_base_type == STOCK:
        # only flows can influence it. we need to find a flow from target structure.
        import_flow_from_target()

    elif start_with_element_base_type in [FLOW, VARIABLE, PARAMETER]:
        # import a {flow, variable, parameter} from target structure
        import_flow_var_param_from_target()

    return new_base


# def chains(structure):
#     structure_chains_generator = chain_decomposition(structure.model_structure.sfd.to_undirected())
#     structure_chains = list()
#     for chain in structure_chains_generator:
#         structure_chains.append(chain)
#     print(structure_chains)
