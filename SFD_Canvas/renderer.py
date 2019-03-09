# SD-simulator
from tkinter import *
from SFD_Canvas.SFD_Canvas import SFDCanvas


def main():
    root = Tk()
    wid = 800
    hei = 600
    Frame1 = SFDCanvas(root)
    root.wm_title("Stock and Flow Canvas")
    root.geometry(str(wid)+"x"+str(hei)+"+300+200")
    root.mainloop()


if __name__ == '__main__':
    main()
