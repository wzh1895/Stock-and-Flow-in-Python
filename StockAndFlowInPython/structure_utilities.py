import networkx as nx
import copy


class StructureUtilities(object):
    @staticmethod
    def calculate_structural_similarity(who_compare, compare_with):
        return

    @staticmethod
    def expand_structure(base_structure, target_structure):
        print('before deep copy:', base_structure)
        base = copy.deepcopy(base_structure)
        print('after deep copy:', base)
        return base
