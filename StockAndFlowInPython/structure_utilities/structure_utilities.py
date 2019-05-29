import networkx as nx
import copy
import random
from networkx.algorithms import chain_decomposition
from StockAndFlowInPython.graph_sd.graph_based_engine import STOCK, FLOW, VARIABLE, PARAMETER


def calculate_structural_similarity(who_compare, compare_with):
    return


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


def new_expand_structure(base_structure, target_structure):
    new_base = copy.deepcopy(base_structure)
    # print("    Base_structure: ", new_base.model_structure.sfd.nodes(data='function', default='Not available'))
    print("    Base_structure: ", new_base.model_structure.sfd.nodes(data='function'))

    # Base

    # get all elements in base structure
    base_structure_elements = list(new_base.model_structure.sfd.nodes)
    # pick an element from base_structure to start with. Now: randomly. Future: guided by activity.
    start_with_element_base = random.choice(base_structure_elements)
    print("    {} in base_structure is chosen to start with".format(start_with_element_base))
    # print("    Details: ", new_base.model_structure.sfd.nodes[start_with_element_base])

    start_with_element_base_type = new_base.model_structure.sfd.nodes[start_with_element_base]['element_type']
    if start_with_element_base_type == STOCK:
        # only flows can influence it. we need to find a flow from target structure.
        all_flows_in_target = target_structure.model_structure.all_flows()
        chosen_flow_name_in_target = random.choice(all_flows_in_target)
        print("    {} in target_structure is chosen to start with".format(chosen_flow_name_in_target))
        # print("    Details: ", target_structure.model_structure.sfd.nodes[chosen_flow_name_in_target])
        chosen_flow_in_target = target_structure.model_structure.sfd.nodes[chosen_flow_name_in_target]

        # build this flow to new_base
        if chosen_flow_in_target['function'] is None:  # the chosen flow is a constant one
            equation = chosen_flow_in_target['value'][0]
        else:  # it has an equation
            equation = chosen_flow_in_target['function']
        x = chosen_flow_in_target['pos'][0]
        y = chosen_flow_in_target['pos'][1]
        flow_from = None
        flow_to = None
        if chosen_flow_in_target['flow_from'] is None and chosen_flow_in_target['flow_to'] is not None:
            flow_from = None
            flow_to = start_with_element_base
        elif chosen_flow_in_target['flow_from'] is not None and chosen_flow_in_target['flow_to'] is None:
            flow_from = start_with_element_base
            flow_to = None
        #TODO there is a third possibility: the chosen flow in target structure connects 2 stocks. Leave for later.
        new_base.build_flow(equation=equation, x=x, y=y, flow_from=flow_from, flow_to=flow_to)

    elif start_with_element_base_type == FLOW:
        pass
    elif start_with_element_base_type == VARIABLE:
        pass
    elif start_with_element_base_type == PARAMETER:
        pass

    return new_base


def chains(structure):
    structure_chains_generator = chain_decomposition(structure.model_structure.sfd.to_undirected())
    structure_chains = list()
    for chain in structure_chains_generator:
        structure_chains.append(chain)
    print(structure_chains)
