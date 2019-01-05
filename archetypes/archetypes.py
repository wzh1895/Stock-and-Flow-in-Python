import networkx as nx
import globalModel as glbele

"""
Archetypes used as basic elements to suggest candidate structures
2 types of archetypes are considered, but not necessarily to be different in nature

    1. Templates: stand alone models
    2. Widgets:   add-ons to stand alone models

We use graph (Graph Theory) to store archetypes.

    Graphs can reflect connectivity of SD models, as CLD;
    Graphs can store extra information for building SFD;
    Graphs themselves can be operated and merged, without translating into SFD.

The following tuples are used to generate Graphs, which could then be used to generate models.

"""

first_order_negative = (('S', 'stock1', 489, 245, '100', 'flow1'),
                        ('F', 'flow1', 381.75, 245, [(285, 245), (466.5, 245)], "(globalElements.get_value('goal1')()-globalElements.get_value('stock1')())/globalElements.get_value('at1')()", ['stock1', 'at1', 'goal1']),
                        ('A', 'at1', 341.5, 156.5, "5"),
                        ('A', 'goal1', 348, 329, "1")
                        )
