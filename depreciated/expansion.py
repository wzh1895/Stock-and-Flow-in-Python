from tkinter import *
from depreciated.suggestion import SuggestionPanel
from StockAndFlowInPython.graph_sd.graph_based_engine import MULTIPLICATION


class ExpansionPanel(SuggestionPanel):
    """
    Main interface for model expansion
    """

    def __init__(self, master):
        super().__init__(master)

        self.fm_expansion = Frame(self.master)
        self.fm_expansion.pack(side=TOP)
        self.btn_start_expansion = Button(self.fm_expansion, text="Start expansion", command=self.expansion_test)
        self.btn_start_expansion.pack(side=LEFT)

        self.expansion_test()

    def expansion_test(self):
        self.session_handler1.show_sfd_window()
        self.session_handler1.show_graph_network_window()
        self.session_handler1.build_stock(name='var1', initial_value=100,
                         # x=289,
                         # y=145
                         )
        self.session_handler1.build_stock(name='var2', initial_value=1)
        self.session_handler1.build_aux(name='fraction0', equation=0.01)
        self.session_handler1.build_aux(name='factor0', equation=[MULTIPLICATION, ['var1', 50], ['var2', 150]])
        self.session_handler1.build_flow(name='flow0', equation=[MULTIPLICATION, ['factor0', 90], ['fraction0', 10]], flow_from='var1', flow_to='var2'
                        # x=181,
                        # y=145,
                        # points=[(85, 145), (266.5, 145)]
                        )
        # self.session_handler1.build_aux(name='fraction0', equation=0.1,
        #                # x=163,
        #                # y=251
        #                )
        # self.session_handler1.build_flow(name='outflow0', equation=5, flow_from='stock0')
        # self.session_handler1.replace_equation(name='outflow0', new_equation=[MULTIPLICATION, ['stock0', 100], ['fraction0', 150]])
        # self.session_handler1.disconnect_stock_flow(flow_name='inflow0', stock_name='stock0')
        # self.session_handler1.disconnect_stock_flow(flow_name='outflow0', stock_name='stock0')
        # self.session_handler1.connect_stock_flow(flow_name='outflow0', new_flow_from='stock0')
        # self.session_handler1.build_aux(name='fraction1', equation=0.1, )
        # self.session_handler1.connect_stock_flow(flow_name='inflow0', new_flow_to='stock0')
        # self.session_handler1.replace_equation(name='inflow0', new_equation=[MULTIPLICATION, ['stock0', 50], ['fraction1', 40]])
        # self.session_handler1.delete_element(name='inflow0')
        # self.session_handler1.delete_element(name='fraction1')
        # self.simulate()


def main():
    root = Tk()
    root.geometry("%dx%d+50+100" % (450, 160))
    root.wm_title("Expansion Test")
    root.configure(background='#fff')
    ExpansionPanel(root)
    root.mainloop()


if __name__ == '__main__':
    main()
