import networkx as nx
import copy
import random
from networkx.algorithms import chain_decomposition
from StockAndFlowInPython.graph_sd.graph_based_engine import Structure, STOCK, FLOW, VARIABLE, PARAMETER, \
    ADDITION, SUBTRACTION, MULTIPLICATION, DIVISION, LINEAR
from StockAndFlowInPython.session_handler import SessionHandler

element_types = [STOCK, FLOW, VARIABLE, PARAMETER]
functions = [ADDITION, SUBTRACTION, MULTIPLICATION, DIVISION, LINEAR]
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


def new_expand_structure(base_structure, start_with_element_base, target_structure):
    print("    **** Building new structure...")
    # new_base = copy.deepcopy(base_structure)
    # print("    Base_structure: ", new_base.model_structure.sfd.nodes(data='function', default='Not available'))
    # new_base = copy.deepcopy(base_structure)
    new_model_structure = Structure(sfd=copy.deepcopy(base_structure.model_structure.sfd),
                                    uid_manager=copy.deepcopy(base_structure.model_structure.uid_manager),
                                    name_manager=copy.deepcopy(base_structure.model_structure.name_manager),
                                    uid_element_name=copy.deepcopy(base_structure.model_structure.uid_element_name))
    new_base = SessionHandler(model_structure=new_model_structure)
    print("    **** Base_structure: ", new_base.model_structure.sfd.nodes(data='function'))

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
            # TODO: if put 0 here, a problem of 0 division may occur.
            equation = 1

        flow_from = None
        flow_to = None
        if chosen_flow_in_target['flow_from'] is None and chosen_flow_in_target['flow_to'] is not None:
            flow_from = None
            flow_to = start_with_element_base
        elif chosen_flow_in_target['flow_from'] is not None and chosen_flow_in_target['flow_to'] is None:
            flow_from = start_with_element_base
            flow_to = None
        # TODO: there is a third possibility: the chosen flow in target structure connects 2 stocks. Leave for later.
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

            elif equation[0] == MULTIPLICATION:
                equation[1] = start_with_element_base
                equation[2] = 1
                uid = new_base.build_aux(equation=equation, x=x, y=y)
                element_name = new_base.model_structure.get_element_name_by_uid(uid)
                new_base.build_connector(from_var=start_with_element_base, to_var=element_name, polarity='positive')

            elif equation[0] == SUBTRACTION:
                factor = random.choice([1, 2])
                equation[factor] = start_with_element_base
                equation[3-factor] = 0
                uid = new_base.build_aux(equation=equation, x=x, y=y)
                element_name = new_base.model_structure.get_element_name_by_uid(uid)
                new_base.build_connector(from_var=start_with_element_base, to_var=element_name,
                                         polarity='positive' if factor == 1 else 'negative'
                                         )

            elif equation[0] == DIVISION:
                factor = random.choice([1, 2])
                equation[factor] = start_with_element_base
                equation[3-factor] = 1
                uid = new_base.build_aux(equation=equation, x=x, y=y)
                element_name = new_base.model_structure.get_element_name_by_uid(uid)
                new_base.build_connector(from_var=start_with_element_base, to_var=element_name,
                                         polarity='positive' if factor == 1 else 'negative'
                                         )

            elif equation[0] == LINEAR:
                equation[1] = start_with_element_base
                uid = new_base.build_aux(equation=equation, x=x, y=y)
                element_name = new_base.model_structure.get_element_name_by_uid(uid)
                new_base.build_connector(from_var=start_with_element_base, to_var=element_name, polarity='positive')

        print("    ****Equation for this new var:", equation)

    # TODO: this mechanism need to be changed, using agent based algorithm
    start_with_element_base_type = new_base.model_structure.sfd.nodes[start_with_element_base]['element_type']
    if start_with_element_base_type == STOCK:
        # only flows can influence it. we need to find a flow from target structure.
        import_flow_from_target()

    elif start_with_element_base_type in [FLOW, VARIABLE, PARAMETER]:
        # import a {flow, variable, parameter} from target structure
        import_flow_var_param_from_target()

    return new_base


def create_causal_link(base_structure):
    print("    **** Creating new causal link...")
    # create a new base structure to modify
    new_model_structure = Structure(sfd=copy.deepcopy(base_structure.model_structure.sfd),
                                    uid_manager=copy.deepcopy(base_structure.model_structure.uid_manager),
                                    name_manager=copy.deepcopy(base_structure.model_structure.name_manager),
                                    uid_element_name=copy.deepcopy(base_structure.model_structure.uid_element_name))
    new_base = SessionHandler(model_structure=new_model_structure)
    print("    **** Base_structure: ", new_base.model_structure.sfd.nodes(data='function'))

    try:
        chosen_var_name_in_base = random.choice(new_base.model_structure.all_certain_type([FLOW, VARIABLE, PARAMETER]))
    except IndexError:
        print("    **** There is still no F/V/P in base structure. Will return base structure as it is.")
        return new_base

    print("    **** {} in target_structure is chosen to start with".format(chosen_var_name_in_base))
    chosen_var_in_base = new_base.model_structure.sfd.nodes[chosen_var_name_in_base]
    # print("    **** Details: ", chosen_var_in_base['function'])

    if chosen_var_in_base['function'] is None:
        # this equation is not a function but a constant
        pass
    else:
        # this equation is a function
        # we need to find the parameter (constant) factor and replace it by an existing S/F/V/P, but not itself or in a short-circuit loop
        function_name = chosen_var_in_base['function'][0]
        arguments = chosen_var_in_base['function'][1:]  # make a copy of the arguments
        print("    Function is {} with arguments {}".format(function_name, arguments))
        try:
            chosen_source_in_base = random.choice(list(new_base.model_structure.sfd.nodes).remove(chosen_var_name_in_base))  # not itself
        except TypeError:
            print("    There are no more element in base_structure {} except for {}".format(new_base.model_structure.sfd.nodes, chosen_var_name_in_base))
            return new_base

        for i in range(len(arguments)):
            # TODO: what implemented here is only 'close the loop', but we need also to consider 'hit the boundary'
            if type(arguments[i]) is int or float:  # if this argument is a constant
                if chosen_source_in_base in arguments:  # not same as the other argument (if there are two)
                    print("    The chosen source is already in the arguments, skip this loop.")
                    break
                else:
                    arguments[i] = chosen_source_in_base
                    if function_name == ADDITION:
                        new_base.build_connector(from_var=chosen_source_in_base, to_var=chosen_var_name_in_base,
                                                 polarity='positive')
                    elif function_name == MULTIPLICATION:
                        new_base.build_connector(from_var=chosen_source_in_base, to_var=chosen_var_name_in_base,
                                                 polarity='positive')
                    elif function_name == SUBTRACTION:
                        new_base.build_connector(from_var=chosen_source_in_base, to_var=chosen_var_name_in_base,
                                                 polarity='positive' if i == 0 else 'negative'
                                                 # y=a-b, a: positive, b: negative
                                                 )
                    elif function_name == DIVISION:
                        new_base.build_connector(from_var=chosen_source_in_base, to_var=chosen_var_name_in_base,
                                                 polarity='positive' if i == 0 else 'negative'
                                                 # y=a / b, a: positive, b: negative
                                                 )
                    elif function_name == LINEAR:
                        pass  # a linear function should not be modified

            else:  # this argument is str (a variable's name)
                pass
        new_function = [function_name] + arguments
        chosen_var_in_base['function'] = new_function  # replace with the changed function

    return base_structure


def apply_a_concept_cld(base_structure, stock_uid_in_base_to_start_with, concept_cld, target_structure):
    print("    **** Applying a concept cld...")
    # create a new base structure to modify
    new_model_structure = Structure(sfd=copy.deepcopy(base_structure.model_structure.sfd),
                                    uid_manager=copy.deepcopy(base_structure.model_structure.uid_manager),
                                    name_manager=copy.deepcopy(base_structure.model_structure.name_manager),
                                    uid_element_name=copy.deepcopy(base_structure.model_structure.uid_element_name))
    new_base = SessionHandler(model_structure=new_model_structure)
    print("    **** Base_structure: ", new_base.model_structure.sfd.nodes(data='function'))

    # TODO: this chain_decomposition function seems not to be very reliable. Replace it with something else in the future
    def generate_chains(structure):
        chains_generator = chain_decomposition(structure.model_structure.sfd.to_undirected())
        chains = list()
        for chain in chains_generator:
            chains.append(chain)
        # print(structure.model_structure.sfd.edges)
        # print(chains)

        # making the chains directed
        for chain in chains:
            for i in range(len(chain)):
                if structure.model_structure.sfd.has_edge(chain[i][0], chain[i][1]):
                    # this edge is stored in the structure in the right direction
                    pass
                elif structure.model_structure.sfd.has_edge(chain[i][1], chain[i][0]):  # just to be safe
                    # this edge is
                    new_joint = (chain[i][1], chain[i][0])
                    chain[i] = new_joint

        # making the chains start from stock
        for j in range(len(chains)):
            new_chain = list()
            # find the joint that start with a stock
            current_joint = None
            for joint in chains[j]:
                if structure.model_structure.sfd.nodes[joint[0]]['element_type'] == STOCK:
                    current_joint = joint
                    break
            for k in range(len(chains[j])):
                new_chain.append(current_joint)
                next_joint_head = current_joint[1]
                for joint in chains[j]:
                    if joint[0] == next_joint_head:
                        current_joint = joint
                        break
            chains[j] = new_chain

        # print(chains)
        return chains

    def decide_chain_polarity(c):
        p = 'positive'
        for joint in c:
            if target_structure.model_structure.sfd.edges[joint]['polarity'] == 'negative':
                if p == 'positive':
                    p = 'negative'
                else:
                    p = 'positive'
                # print("polarity changed to", p)
        return p

    # The idea here, is to use the concept CLD to guide the extraction of elements from the target structure and the
    # addition of these elements to the base structure.

    # Analyze the target structure to find all the feedback loops
    chains_in_target = generate_chains(target_structure)

    # Chances are there is no chain in target structure / there are multiple chains in target structure
    if len(chains_in_target) == 0:  # There is no chain in target, so do nothing
        return new_base
    else:  # Use the concept CLD to instruct importing elements from target to base structure
        # Preparation
        print("    1. Which stock to start in the base structure?", stock_uid_in_base_to_start_with)
        print("    2. Which concept CLD to follow?\n       {}".format(concept_cld.edges))
        print("       This concept CLD has {} loop.".format(concept_cld.graph['polarity']))
        print("    3. Which chain to use in target structure?")
        chosen_chain_in_target = None
        # TODO: now we use the first-met suitable chain, and only decide by polarity. Update needed in the future.
        for chain in chains_in_target:
            polarity = decide_chain_polarity(chain)
            # print("Chain polarity:", polarity)
            if polarity == concept_cld.graph['polarity']:
                chosen_chain_in_target = chain
                break
        print("       {}".format(chosen_chain_in_target))
        if chosen_chain_in_target is None:
            print("    Could not find a suitable chain in target to operate. Aborting.")
            return new_base

        # Iterate over the concept CLD to import elements from target to base
        current_node_in_concept_cld = STOCK  # TODO: need to update, because in a concept CLD there could be >1 nodes
        current_joint_in_target_chain = chosen_chain_in_target[0]

        # a dict storing the 3 currently focused joints/element
        structure_operating = {'concept': current_node_in_concept_cld,
                             'target': current_joint_in_target_chain,
                             'base': stock_uid_in_base_to_start_with,
                             }

        continue_mapping = True
        continue_building = True

        while continue_mapping:
            # Check if current [element in base] fits current [joint in concept]

            func = new_base.model_structure.get_element_by_uid(structure_operating['base'])['function']
            if func is None:
                check = False
            else:
                if func[0] == structure_operating['concept']:
                    check = True
                else:
                    check = False

            if (structure_operating['concept'] in element_types and
                new_base.model_structure.get_element_by_uid(structure_operating['base'])['element_type'] == structure_operating['concept']) \
                    or (structure_operating['concept'] in functions and check):
                print("    Success 1: concept CLD's node matches the element in base structure.")

                # move forward on concept cld
                structure_operating['concept'] = list(concept_cld.successors(structure_operating['concept']))[0]
                print("    Moved to the next element in concept cld: ", structure_operating['concept'])

                # check if in base structure, the focused element has a successor
                successors_in_base = list(new_base.model_structure.sfd.successors(new_base.model_structure.get_element_name_by_uid(structure_operating['base'])))
                if len(successors_in_base) == 0:
                    print("    In base structure the current element has no successor, stop mapping.")
                    continue_mapping = False
                else:
                    # TODO: in future need to select when there are more loops. Consider chains/ paths.
                    structure_operating['base'] = successors_in_base[0]
            else:
                print("    Not fit: {} and {}, stop mapping.".format(structure_operating['concept'], structure_operating['base']))
                continue_mapping = False

        while continue_building:
            # Iterate along the target chain to find a node that fits the current element in concept cld
            continue_seeking = True
            print("Here 1,", target_structure.model_structure.sfd.nodes[structure_operating['target'][0]])
            while continue_seeking:

                func = target_structure.model_structure.sfd.nodes[structure_operating['target'][0]]['function']
                if func is None:
                    print("Here 1.5")
                    check = False
                else:
                    print("Here 2,", func[0], structure_operating['concept'])
                    if func[0] == structure_operating['concept']:
                        check = True
                    else:
                        check = False

                if (structure_operating['concept'] in element_types and
                    target_structure.model_structure.sfd.nodes[structure_operating['target'][0]]['element_type'] == structure_operating['concept']) \
                        or (structure_operating['concept'] in functions and check):
                    print("    Success 2: concept CLD's node matches the element in target structure.")
                    continue_seeking = False  # Time to build
                else:
                    # replace 'target' in structure_operating with the next joint in chain
                    idx = chosen_chain_in_target.index(structure_operating['target']) + 1
                    try:
                        structure_operating['target'] = chosen_chain_in_target[idx]
                    except IndexError:
                        # The chain has been looped up and no fitting element is found
                        print("    Failure: Cannot find a fitting element in target chain.")
                        return new_base

            # Import the target chain's current element into base_structure


            continue_building = False

            print("Finally,", structure_operating)

        return new_base
