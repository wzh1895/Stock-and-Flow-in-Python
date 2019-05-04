import random
from tkinter import *
from suggestion import SuggestionPanel
from StockAndFlowInPython.graph_sd.graph_based_engine import STOCK, FLOW, VARIABLE, PARAMETER, CONNECTOR, ALIAS, MULTIPLICATION, LINEAR


class ExpansionPanel(SuggestionPanel):
    """
    Main utility for model expansion
    """
    def __init__(self, master):
        super().__init__(master)

        self.fm_expansion = Frame(self.master)
        self.fm_expansion.pack(side=TOP)
        self.btn_start_expansion = Button(self.fm_expansion, text="Start expansion", command=self.start_expansion)
        self.btn_start_expansion.pack(side=LEFT)

        self.start_expansion()

    def start_expansion(self):
        self.session_handler1.show_sfd_window()
        self.session_handler1.show_graph_network_window()
        self.build_stock(name='stock0', initial_value=1,
                         # x=289,
                         # y=145
                         )

        self.build_flow(name='flow0', equation=1, flow_to='stock0',
                        # x=181,
                        # y=145,
                        points=[(85, 145), (266.5, 145)])
        # self.build_flow(name='flow0', equation=[LINEAR, ['stock0', 100]], flow_to='stock0',
        #                 #x=181,
        #                 #y=145,
        #                 points=[(85, 145), (266.5, 145)]
        #                 )

        self.build_aux(name='fraction0', equation=0.1,
                        # x=163,
                        # y=251
                        )


        self.build_flow(name='outflow0', equation=[MULTIPLICATION, ['stock0', 100], ['fraction0', 150]], flow_from='stock0')

        # self.simulate()

    def build_stock(self, name, initial_value, x=0, y=0):
        """
        Build a stock in the way a modeler will do.
        :param name: The stock's name
        :param initial_value: Th e stock's initial value
        :param x: X coordinate in the canvas
        :param y: Y coordinate in the canvas
        :return:
        """
        print("\nBuilding stock {}\n".format(name))
        if x == 0 or y == 0:  # if x or y not specified, automatically generate it.
            pos = self.generate_location(self.session_handler1.sfd_window1, [])
            x = pos[0]
            y = pos[1]
            print("Generated position for {} at x = {}, y = {}.".format(name, x, y))
        self.session_handler1.sess1.add_stock(name=name, equation=[initial_value], x=x, y=y)
        self.session_handler1.refresh()
        self.variables_list['values'] = self.session_handler1.variables_in_model

    def build_flow(self, name, equation, x=0, y=0, points=list(), flow_from=None, flow_to=None):
        """
        Build a flow in the way a modeler will do.
        :param name: The flow's name
        :param equation: The flow's equation
        :param x: X coordinate in the canvas
        :param y: Y coordination in the canvas
        :param points: Starting, ending and all bending points in between
        :param flow_from: Outflow from ...
        :param flow_to: Inflow to ...
        :return:
        """
        print("\nBuilding flow {}\n".format(name))

        linked_vars = list()  # collect linked variables for generating location
        if type(equation) is int or type(equation) is float:  # if equation is number, wrap it into []
            equation = [equation]
        else:
            for linked_var in equation[1:]:  # loop all parameters the function takes
                if type(linked_var) is list:  # it's a name+angle instead of a number
                    linked_vars.append(linked_var[0])  # add the name to 'linked_vars'
        print(name, 'is linked to', linked_vars)

        if x == 0 or y == 0:  # if x or y not specified, automatically generate it.
            pos = self.generate_location(self.session_handler1.sfd_window1, linked_vars)
            x = pos[0]
            y = pos[1]

            # However, because a flow is assumed to be horizontally aligned with its in/out stock, then
            # 1) if it is only linked to one stock, stock's y -> flow's y
            # 2) if it is linked to 2 stocks, flow -> right in between them

            if flow_from is not None and flow_to is not None:
                print("This flow influences 2 stocks")
                x = self.session_handler1.sess1.structures['default'].get_coordinate(flow_from)[0]+\
                    self.session_handler1.sess1.structures['default'].get_coordinate(flow_to)[0]
                y = self.session_handler1.sess1.structures['default'].get_coordinate(flow_from)[1]+\
                    self.session_handler1.sess1.structures['default'].get_coordinate(flow_to)[1]
            elif flow_from is not None:
                print("This flow flows from {}".format(flow_from))
                y = self.session_handler1.sess1.structures['default'].get_coordinate(flow_from)[1]
                x = self.session_handler1.sess1.structures['default'].get_coordinate(flow_from)[0] + 107
            elif flow_to is not None:
                print("This flow flows to {}".format(flow_to))
                y = self.session_handler1.sess1.structures['default'].get_coordinate(flow_to)[1]
                x = self.session_handler1.sess1.structures['default'].get_coordinate(flow_to)[0] - 107

            # Points need to be generated as well
            # calculating using: x=181, y=145, points=[(85, 145), (266.5, 145)]
            points = [(x-85.5, y), (x+85.5, y)]

            print("Generated position for {} at x = {}, y = {}.".format(name, x, y))

        self.session_handler1.sess1.add_flow(name=name,
                                             equation=equation,
                                             flow_from=flow_from,
                                             flow_to=flow_to,
                                             x=x,
                                             y=y,
                                             points=points)
        self.session_handler1.refresh()
        self.variables_list['values'] = self.session_handler1.variables_in_model

    def build_aux(self, name, equation, x=0, y=0):
        """
        Build an auxiliary variable in the way a modeler will do.
        :param name: The variable's name
        :param equation: The variable's equation
        :param x: X coordinate in the canvas
        :param y: Y coordinate in the canvas
        :return:
        """
        print("\nBuilding aux {}\n".format(name))

        linked_vars = list()  # collect linked variables for generating location
        if type(equation) is int or type(equation) is float:  # if equation is number, wrap it into []
            equation = [equation]
        else:
            for linked_var in equation[1:]:  # loop all parameters the function takes
                if type(linked_var) is list:  # it's a name instead of a number
                    linked_vars.append(linked_var[0])
        print(name, 'is linked to', linked_vars)

        if x == 0 or y == 0:  # if x or y not specified, automatically generate it.
            pos = self.generate_location(self.session_handler1.sfd_window1, linked_vars)
            x = pos[0]
            y = pos[1]
            print("Generated position for {} at x = {}, y = {}.".format(name, x, y))

        self.session_handler1.sess1.add_aux(name=name,
                                            equation=equation,
                                            x=x,
                                            y=y)
        self.session_handler1.refresh()
        self.variables_list['values'] = self.session_handler1.variables_in_model

    def generate_location(self, sfd_window, linked_vars):
        """
        Automatically decide where to put a variable.
        :param sfd_window: The canvas object where this var is going to be put on
        :param linked_vars: A list of variables that are linked to this new var
        :return: A x-y coordinate for the new variable
        """
        sfd_window.top.update()
        canvas_width = sfd_window.top.winfo_width()
        canvas_height = sfd_window.top.winfo_height()

        # When it is isolated: centered
        if len(linked_vars) == 0:
            print("Generating location. Isolated.")
            base_x = canvas_width/2
            base_y = canvas_height/2
            random_range = 90
            return random.randint(base_x - random_range, base_x + random_range), \
                   random.randint(base_y - random_range, base_y + random_range)
        # When it is linked to only one exiting variable: somewhere around it
        elif len(linked_vars) == 1:
            print("Generating location. Linked to one variable.")
            base_x = self.session_handler1.sess1.structures['default'].get_coordinate(linked_vars[0])[0]
            base_y = self.session_handler1.sess1.structures['default'].get_coordinate(linked_vars[0])[1]
            random_range = 80
            return random.randint(base_x - random_range, base_x + random_range), \
                   random.randint(base_y - random_range, base_y + random_range)
        # when it is linked to 2 or more variables: somewhere around the geometric center
        else:
            base_x = base_y = 0
            print("Generating location. Linked to {} variables.".format(len(linked_vars)))
            for linked_var in linked_vars:
                base_x += self.session_handler1.sess1.structures['default'].get_coordinate(linked_var)[0]
                base_y += self.session_handler1.sess1.structures['default'].get_coordinate(linked_var)[1]
            base_x = round(base_x/len(linked_vars))
            base_y = round(base_y/len(linked_vars))
            random_range = 100
            return random.randint(base_x - random_range, base_x + random_range), \
                   random.randint(base_y - random_range, base_y + random_range)


def main():
    root = Tk()
    expansion_test1 = ExpansionPanel(root)
    root.wm_title("Expansion Test")
    root.geometry("%dx%d+50+100" % (485, 160))
    root.configure(background='#fff')
    root.mainloop()


if __name__ == '__main__':
    main()
