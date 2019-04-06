"""
Controller tool bar for this entire project
"""

from tkinter import *
from tkinter import ttk
from StockAndFlowInPython.session_handler import SessionHandler


class ControllerBar(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack(fill=BOTH, expand=1)

        self.session_handler1 = SessionHandler()

        self.lb_name = Label(self.master, text='System Dynamics Model', background="#fff")
        self.lb_name.pack(side=TOP)
        self.fm_1 = Frame(self.master)
        self.fm_1.pack(side=TOP)
        self.btn_load_model = Button(self.fm_1, text="Load model", command=self.file_load)
        self.btn_load_model.pack(side=LEFT)
        self.btn_run = Button(self.fm_1, text="Simulate", command=self.simulate)
        self.btn_run.pack(side=LEFT)
        self.variables_list = ttk.Combobox(self.fm_1)
        self.variables_in_model = ["Variable"]
        self.variables_list["values"] = self.variables_in_model
        self.variables_list.current(0)
        self.variables_list.bind("<<ComboboxSelected>>", self.select_variable)
        self.variables_list.pack(side=LEFT)
        self.sim_time = StringVar()
        self.sim_time.set("20")
        self.entry1 = Entry(self.fm_1, width=10, textvariable=self.sim_time)
        self.entry1.pack()

        self.fm_2 = Frame(self.master)
        self.fm_2.pack(side=TOP)
        self.btn_show_result = Button(self.fm_2, text="Show result", command=self.session_handler1.show_result)
        self.btn_show_result.pack(side=LEFT)
        self.btn_reset = Button(self.fm_2, text="Reset", command=self.session_handler1.reset)
        self.btn_reset.pack(side=LEFT)
        self.btn_clear_run = Button(self.fm_2, text="Clear a run", command=self.session_handler1.clear_a_run)
        self.btn_clear_run.pack(side=LEFT)
        self.btn_refresh = Button(self.fm_2, text="Refresh", command=self.session_handler1.refresh)
        self.btn_refresh.pack(side=LEFT)

    def simulate(self):
        self.session_handler1.simulation_handler(simulation_time=int(self.entry1.get()))

    def file_load(self):
        file_name_and_variables = self.session_handler1.file_load()
        print(file_name_and_variables)
        file_name = file_name_and_variables[0]
        variables_in_model = file_name_and_variables[1]
        print("variables in model:", variables_in_model)
        print("file name:", file_name)
        if file_name != '':
            self.lb_name.config(text=file_name)
            self.variables_list['values'] = variables_in_model

    def select_variable(self, *args):
        print(self.variables_list.get())
        self.session_handler1.selected_variable = self.variables_list.get()


def main():
    root = Tk()
    controller_bar1 = ControllerBar(root)
    root.wm_title("Controller")
    root.geometry("%dx%d+50+100" % (485, 80))
    root.configure(background='#fff')
    root.mainloop()


if __name__ == '__main__':
    main()
