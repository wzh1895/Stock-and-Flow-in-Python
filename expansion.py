"""
main utility for model expansion
"""

from tkinter import *
from suggestion import SuggestionPanel
from StockAndFlowInPython.Graph_SD.graph_based_engine import MULTIPLICATION, LINEAR


class ExpansionPanel(SuggestionPanel):
    def __init__(self, master):
        super().__init__(master)

        self.session_handler1.show_sfd_window()
        self.session_handler1.show_graph_network_window()
        self.build_stock(name='stock0', initial_value=1, x=289, y=145)

        self.build_flow(name='flow0', equation=[1], flow_to='stock0', x=181, y=145, points=[(85, 145), (266.5, 145)])
        #self.build_flow(name='flow0', equation=[LINEAR, ['stock0', 100]], flow_to='stock0', x=181, y=145, points=[(85, 145), (266.5, 145)])

        # self.build_aux(name='fraction0', equation=0.1, x=163, y=251)

        self.simulate()

    def build_stock(self, name, initial_value, x, y):
        self.session_handler1.sess1.add_stock(name=name, equation=[initial_value], x=x, y=y)
        self.session_handler1.refresh()
        self.variables_list['values'] = self.session_handler1.variables_in_model

    def build_flow(self, name, equation, x, y, points, flow_from=None, flow_to=None):
        self.session_handler1.sess1.add_flow(name=name,
                                             equation=equation,
                                             flow_from=flow_from,
                                             flow_to=flow_to,
                                             x=x,
                                             y=y,
                                             points=points)
        self.session_handler1.refresh()
        self.variables_list['values'] = self.session_handler1.variables_in_model

    def build_aux(self, name, equation, x, y):
        self.session_handler1.sess1.add_aux(name=name, equation=[equation], x=x, y=y)
        self.session_handler1.refresh()
        self.variables_list['values'] = self.session_handler1.variables_in_model


def main():
    root = Tk()
    expansion_test1 = ExpansionPanel(root)
    root.wm_title("Expansion Test")
    root.geometry("%dx%d+50+100" % (485, 160))
    root.configure(background='#fff')
    root.mainloop()


if __name__ == '__main__':
    main()
