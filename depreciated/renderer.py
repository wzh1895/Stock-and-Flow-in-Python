# SD-simulator
from tkinter import *
from StockAndFlowInPython.sfd_canvas.sfd_canvas_tkinter import SFDCanvas

def main():
    root = Tk()
    wid = 800
    hei = 600
    Frame1 = SFDCanvas(root)
    root.wm_title("Stock and Flow Canvas")
    root.geometry("%dx%d+100+100" % (wid, hei))
    root.configure(background='#fff')
    root.mainloop()


if __name__ == '__main__':
    main()
