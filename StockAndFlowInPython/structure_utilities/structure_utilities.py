import networkx as nx
import copy
import random
import numpy as np
import matplotlib.pyplot as plt
from networkx.algorithms import chain_decomposition
from StockAndFlowInPython.graph_sd.graph_based_engine import Structure, STOCK, FLOW, VARIABLE, PARAMETER, \
    ADDITION, SUBTRACTION, MULTIPLICATION, DIVISION, LINEAR
from StockAndFlowInPython.session_handler import SessionHandler
from StockAndFlowInPython.behaviour_utilities.behaviour_utilities import similarity_calc_behavior, similarity_calc_pattern

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

    # TODO: this mechanism need to be updated, using agent based algorithm
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
        return new_base  # by using 'return', we accommodate 'failure'.
    else:  # Use the concept CLD to instruct importing elements from target to base structure
        # Preparation
        print("    1. Which stock to start in the base structure? uid:", stock_uid_in_base_to_start_with)
        print("    2. Which concept CLD to follow?\n       {}".format(concept_cld.edges))
        print("       This concept CLD has {} loop.".format(concept_cld.graph['polarity']))
        print("    3. Which chain to use in target structure?")
        chosen_chain_in_target = None
        # TODO: now we use the first-met suitable chain, and only decide by polarity. Update needed in the future.
        for chain in chains_in_target:
            polarity = decide_chain_polarity(chain)
            # print("Chain polarity:", polarity)
            if polarity == concept_cld.graph['polarity']:
                chosen_chain_in_target = chain  # use the first-met one
                break
        print("       {}".format(chosen_chain_in_target))
        if chosen_chain_in_target is None:
            print("    Could not find a suitable chain in target to operate. Aborting.")
            return new_base

        # Iterate over the concept CLD to import elements from target to base
        current_node_in_concept_cld = concept_cld.graph['begin_with']  # TODO: need to update, because in a concept CLD there could be >1 stocks
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

            # Use this check to see if the element in base has the needed function in concept cld
            print('bbb', structure_operating)
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
                    structure_operating['base'] = new_base.model_structure.sfd.nodes[successors_in_base[0]]['uid']  #
            else:
                print("    Not fit: {} and {}, stop mapping.".format(structure_operating['concept'], structure_operating['base']))
                continue_mapping = False

        while continue_building:
            # step 1 seeking: Iterate along the target chain to find a node that fits the current element in concept cld
            continue_seeking = True
            print("Here 1,", target_structure.model_structure.sfd.nodes[structure_operating['target'][0]])
            while continue_seeking:

                # Use this check to see if the element in base has the needed function in concept cld
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
                    # replace 'target' in structure_operating with the next joint in chain / move forward on target chain
                    idx = chosen_chain_in_target.index(structure_operating['target']) + 1
                    try:
                        # move forward on target chain.
                        structure_operating['target'] = chosen_chain_in_target[idx]
                    except IndexError:
                        # The chain has been looped up and no fitting element is found
                        print("    Failure: Cannot find a fitting element in target chain.")
                        return new_base

            # In building, there are two possibilities: \
            # 1) the needed element already exists as a result of other building activities (e.g. randomly importing) \
            #    In this case, we don't import a new element but incorporate it in this new loop.
            # 2) the needed element doesn't exist in this base structure. In this case, we have to import it.
            # step 2a : Iterate in current 'base' to find if there has already been an 'stand alone' element that fits.
            already_existing = False
            print('Inc0', structure_operating['concept'])
            if structure_operating['concept'] in element_types:
                # we need to look for this type of element in base. TODO: we do not consider this part right now. Currently only focus on functions.
                all_this_type_in_base = new_base.model_structure.all_certain_type(structure_operating['concept'])
                if len(all_this_type_in_base) == 0:  # there still hasn't been an element in base of such type
                    pass
                else:  # there is at least one element in base of such type.
                    pass
            elif structure_operating['concept'] in functions:
                # we need to look for this type of function in base.
                element_functions = nx.get_node_attributes(new_base.model_structure.sfd, 'function')
                print('Inc1', element_functions)
                for element_name, element_function in element_functions.items():
                    if type(element_function) == list:  # then it's not None
                        if element_function[0] == structure_operating['concept']:  # this element has the function that demanded by the concept cld
                            # Incorporate this element into the loop we are building, instead of importing from generic structue
                            print("    Incorporating existing element in base into loop...")
                            start_with_element_base = new_base.model_structure.get_element_name_by_uid(structure_operating['base'])
                            new_base.model_structure.sfd.nodes[element_name]['function'][1] = start_with_element_base
                            print('Inc2', element_name, new_base.model_structure.sfd.nodes[element_name])
                            new_base.build_connector(from_var=start_with_element_base, to_var=element_name,
                                                     polarity='positive'
                                                     )
                            # get the uid of this existing element, to let structure_operating to move forward on base
                            uid = new_base.model_structure.sfd.nodes[element_name]['uid']
                            # Change the flag 'already_existing' to True, so no need to import from generic structure
                            already_existing = True
                            break  # now that we have found what we need from base, stop this loop

            # step 2b : If not found, import the target chain's current element into base_structure
            if not already_existing:
                # Because we consider only loop/chain in this utility, so what imported must have a function
                # TODO: in future when there are >1 order loops, may be different
                print("    Starting building new element in base...")
                start_with_element_base = new_base.model_structure.get_element_name_by_uid(structure_operating['base'])
                print("    **** Element in base to build on:", start_with_element_base)
                chosen_var_in_target = target_structure.model_structure.sfd.nodes[structure_operating['target'][0]]
                print("    **** Details of element to import:", chosen_var_in_target)

                x = chosen_var_in_target['pos'][0]
                y = chosen_var_in_target['pos'][1]

                if chosen_var_in_target['function'] is None:  # the chosen var is a constant => Parameter  #TODO: now it's impossible for this to be Parameter, but save for later
                    equation = chosen_var_in_target['value'][0]
                else:  # it has a function as equation
                    # Not just copy-paste the equation; but to modify its parameters to constants

                    equation = copy.deepcopy(chosen_var_in_target['function'])

                    if equation[0] == ADDITION:
                        equation[1] = start_with_element_base
                        equation[2] = 0
                        uid = new_base.build_aux(equation=equation, x=x, y=y)
                        element_name = new_base.model_structure.get_element_name_by_uid(uid)
                        new_base.build_connector(from_var=start_with_element_base, to_var=element_name,
                                                 polarity='positive')

                    elif equation[0] == MULTIPLICATION:
                        equation[1] = start_with_element_base
                        equation[2] = 1
                        uid = new_base.build_aux(equation=equation, x=x, y=y)
                        element_name = new_base.model_structure.get_element_name_by_uid(uid)
                        new_base.build_connector(from_var=start_with_element_base, to_var=element_name,
                                                 polarity='positive')

                    elif equation[0] == SUBTRACTION:
                        # TODO: mechanism to decide if a-b or b-a
                        # factor = random.choice([1, 2])
                        equation[1] = start_with_element_base
                        equation[2] = 0
                        uid = new_base.build_aux(equation=equation, x=x, y=y)
                        element_name = new_base.model_structure.get_element_name_by_uid(uid)
                        new_base.build_connector(from_var=start_with_element_base, to_var=element_name,
                                                 polarity='positive'
                                                 )

                    elif equation[0] == DIVISION:
                        # TODO: mechanism to decide if a /b or b /a
                        # factor = random.choice([1, 2])
                        equation[1] = start_with_element_base
                        equation[2] = 1
                        uid = new_base.build_aux(equation=equation, x=x, y=y)
                        element_name = new_base.model_structure.get_element_name_by_uid(uid)
                        new_base.build_connector(from_var=start_with_element_base, to_var=element_name,
                                                 polarity='positive'
                                                 )

                    elif equation[0] == LINEAR:
                        equation[1] = start_with_element_base
                        uid = new_base.build_aux(equation=equation, x=x, y=y)
                        element_name = new_base.model_structure.get_element_name_by_uid(uid)
                        new_base.build_connector(from_var=start_with_element_base, to_var=element_name,
                                                 polarity='positive')

            # move forward on base_structure
            structure_operating['base'] = uid

            # move forward on concept cld
            structure_operating['concept'] = list(concept_cld.successors(structure_operating['concept']))[0]
            print("    Moved to the next element in concept cld: ", structure_operating['concept'])

            # if this element from the concept cld is identical to the starting
            # TODO: need to update for conditions with more than 1 stock
            if structure_operating['concept'] == concept_cld.graph['end_with']:
                # close the loop by confirm connection from the last added var to stock
                # 2 steps: 1) create a flow and 2) make it equivalent to the last added var
                polarity_f_s = concept_cld.edges[list(concept_cld.in_edges(structure_operating['concept']))[0]]['polarity']
                f_uid = new_base.build_flow(equation=[LINEAR, new_base.model_structure.get_element_name_by_uid(structure_operating['base'])],
                                            flow_from=new_base.model_structure.get_element_name_by_uid(stock_uid_in_base_to_start_with) if polarity_f_s == 'negative' else None,
                                            flow_to=new_base.model_structure.get_element_name_by_uid(stock_uid_in_base_to_start_with) if polarity_f_s == 'positive' else None,
                                            x=120 if polarity_f_s == 'positive' else 302,
                                            y=172,
                                            points=[[49, 172], [191, 172]] if polarity_f_s == 'positive' else [[236, 171], [392, 171]]
                                            )
                new_base.build_connector(from_var=new_base.model_structure.get_element_name_by_uid(structure_operating['base']),
                                         to_var=new_base.model_structure.get_element_name_by_uid(f_uid),
                                         polarity='positive')
                # stop building
                continue_building = False

            print("Finally,", structure_operating)
            print("Finally2,", new_base.model_structure.sfd.nodes(data='function'))

        return new_base


class ParameterIdPosManager(object):
    def __init__(self):
        self.param_id = 0
        self.param_x = 30
        self.param_y = 30

    def get_new_pid_pos(self):
        self.param_id += 1
        self.param_x += 80
        return self.param_id, self.param_x, self.param_y


def optimize_parameters(base_structure, reference_modes, reference_mode_bindings):
    print("    **** Optimizing parameters...")
    # create a new base structure to modify
    new_model_structure = Structure(sfd=copy.deepcopy(base_structure.model_structure.sfd),
                                    uid_manager=copy.deepcopy(base_structure.model_structure.uid_manager),
                                    name_manager=copy.deepcopy(base_structure.model_structure.name_manager),
                                    uid_element_name=copy.deepcopy(base_structure.model_structure.uid_element_name))
    new_base = SessionHandler(model_structure=new_model_structure)
    print("    **** Base_structure: ", new_base.model_structure.sfd.nodes(data='function'))

    parameter_id_pos_manager = ParameterIdPosManager()
    parameter_id = dict()  # parameter_id : uid

    # search all functions and derive parameters (standalone variables) for them
    for element_name in list(new_base.model_structure.sfd.nodes):
        element_properties = new_base.model_structure.sfd.nodes[element_name]
        if element_properties['function'] is not None:
            func = element_properties['function']
            print("Opti0", func)
            params = func[1:]  # this is a copy, so we need an additional step to change the original function[]

            for i in range(len(params)):
                print("Opti1", params[i])
                if type(params[i]) in [int, float]:
                    # 1) generate a new parameter
                    pid, px, py = parameter_id_pos_manager.get_new_pid_pos()
                    uid = new_base.build_aux(equation=params[i], x=px, y=py)

                    # 2) index this new parameter by pid
                    parameter_id[pid] = uid

                    # 3) replace this parameter
                    func[i+1] = new_base.model_structure.get_element_name_by_uid(uid)  # change func instead of params
                    new_base.build_connector(from_var=new_base.model_structure.get_element_name_by_uid(uid),
                                             to_var=element_name
                                             )

    # hyper params
    rnd = 10
    epoch = 5

    distance_old = 100
    distance_new = 0

    param_history = dict()
    param_alpha = {1: 1, 2: 0.2}

    for param_id, param_element_uid in parameter_id.items():
        param_history[param_id] = [new_base.model_structure.get_element_by_uid(param_element_uid)['value'][0]]

    for i in range(rnd):
        print('\nRound {}'.format(i))
        for param_id, param_element_uid in parameter_id.items():
            print('\nParameter {} value {}'.format(new_base.model_structure.get_element_name_by_uid(uid),
                                                 new_base.model_structure.get_element_by_uid(uid)['value'][0]))
            adjustment_direction = 1
            # optimizing one parameter

            for j in range(epoch):
                print('\nEpoch', j)

                print("Simulating...")
                new_base.simulation_handler(25)

                distance_new = 0

                for reference_mode_name, reference_mode_property in reference_modes.items():
                    bound_element_uid = reference_mode_bindings[reference_mode_name]
                    who_compare = new_base.model_structure.get_element_by_uid(bound_element_uid)['value']
                    compare_with = reference_mode_property[1]
                    distance_new += similarity_calc_behavior(np.array(who_compare).reshape(-1, 1),
                                                             np.array(compare_with).reshape(-1, 1))[0]

                if abs(distance_new - distance_old) < 0.0001:
                    print('    Distance small enough')
                    break

                if distance_new <= distance_old:  # if getting closer to optimum
                    print('    Getting closer {}\n'.format(distance_new))
                else:
                    print('    Getting farther {}\n'.format(distance_new))
                    adjustment_direction *= (-1)  # change direction

                distance_old = distance_new

                print("here!", new_base.model_structure.get_element_name_by_uid(param_element_uid))
                print("here!", new_base.model_structure.get_element_by_uid(param_element_uid)['value'][0])
                new_param_value = new_base.model_structure.get_element_by_uid(param_element_uid)['value'][0] + param_alpha[param_id] * adjustment_direction
                new_base.model_structure.get_element_by_uid(param_element_uid)['value'][0] = new_param_value
                print("here!", new_base.model_structure.get_element_by_uid(param_element_uid)['value'][0])
                param_history[param_id].append(new_param_value)

        print("Opti6", "Distance", distance_old)

    for param_id, p_history in param_history.items():
        plt.plot(p_history, label=new_base.model_structure.get_element_name_by_uid(parameter_id[param_id]))
    plt.show()

    return new_base
