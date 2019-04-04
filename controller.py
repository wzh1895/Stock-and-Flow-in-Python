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

        self.lb = Label(self.master, text='Display System Dynamics Model', background="#fff")
        self.lb.pack(side=TOP)
        self.fm_1 = Frame(self.master)
        self.fm_1.pack(side=TOP)
        self.btn1 = Button(self.fm_1, text="Load model", command=self.file_load)
        self.btn1.pack(side=LEFT)
        self.btn_run = Button(self.fm_1, text="Run", command=self.simulate)
        self.btn_run.pack(side=LEFT)
        self.comboxlist = ttk.Combobox(self.fm_1)
        self.variables_in_model = ["Variable"]
        self.comboxlist["values"] = self.variables_in_model
        self.comboxlist.current(0)
        self.comboxlist.bind("<<ComboboxSelected>>", self.select_variable)
        self.comboxlist.pack(side=LEFT)
        self.sim_time = StringVar()
        self.sim_time.set("13")
        self.entry1 = Entry(self.fm_1, width=10, textvariable=self.sim_time)
        self.entry1.pack()

        self.fm_2 = Frame(self.master)
        self.fm_2.pack(side=TOP)
        self.btn3 = Button(self.fm_2, text="Show result", command=self.session_handler1.show_result)
        self.btn3.pack(side=LEFT)
        self.btn4 = Button(self.fm_2, text="Reset", command=self.session_handler1.reset)
        self.btn4.pack(side=LEFT)
        self.btn5 = Button(self.fm_2, text="Clear a run", command=self.session_handler1.clear_a_run)
        self.btn5.pack(side=LEFT)

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
            self.lb.config(text=file_name)
            self.comboxlist['values'] = variables_in_model

    def select_variable(self, *args):
        print(self.comboxlist.get())
        self.session_handler1.selected_variable = self.comboxlist.get()


def main():
    root = Tk()
    wid = 480
    hei = 80
    controller_bar1 = ControllerBar(root)
    root.wm_title("Controller")
    root.geometry("%dx%d+100+100" % (wid, hei))
    root.configure(background='#fff')
    root.mainloop()


if __name__ == '__main__':
    main()
