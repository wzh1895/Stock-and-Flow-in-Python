"""
main utility for model expansion
"""

from tkinter import *
from controller import ControllerBar


def main():
    root = Tk()
    expansion_test1 = ControllerBar(root)
    root.wm_title("Expansion Test")
    root.geometry("%dx%d+100+100" % (expansion_test1.wid, expansion_test1.hei))
    root.configure(background='#fff')
    root.mainloop()


if __name__ == '__main__':
    main()
