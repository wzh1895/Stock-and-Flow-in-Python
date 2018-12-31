"""
Main function of Concepta
"""

from tkinter import *

class Panel(Frame):
    def __init__(self,master):
        super().__init__(master)
        self.master = master
        self.pack(fill=BOTH,expand=1)

if __name__ == '__main__':
    root = Tk()
    wid = 1152
    hei = 864
    root.wm_title("Conceptualization Panel")
    root.geometry(str(wid)+"x"+str(hei)+"+100+100")
    Panel = Panel(root)
    root.mainloop()
