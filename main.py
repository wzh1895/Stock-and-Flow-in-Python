import tkinter as tk
from canvasSrc import SFDCanvas

def main():
    root = tk.Tk()
    ex = SFDCanvas()
    root.geometry("1280x960+200+100")
    root.mainloop()

if __name__ == '__main__':
    main()
