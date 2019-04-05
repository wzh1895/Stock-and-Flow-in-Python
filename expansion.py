"""
main utility for model expansion
"""

from tkinter import *
from suggestion import SuggestionPanel


class ExpansionPanel(SuggestionPanel):
    def __init__(self, master, wid, hei):
        super().__init__(master, wid, hei)


def main():
    root = Tk()
    expansion_test1 = ExpansionPanel(root, 485, 160)
    root.wm_title("Expansion Test")
    root.geometry("%dx%d+100+100" % (expansion_test1.wid, expansion_test1.hei))
    root.configure(background='#fff')
    root.mainloop()


if __name__ == '__main__':
    main()
