import tkinter as tk
import math

class SFDCanvas(tk.Frame):
    def __init__(self):
        tk.Frame.__init__(self)
        self.initUI()

    def initUI(self):
        self.master.title("Stock and Flow Canvas")
        self.pack(fill=tk.BOTH, expand=1)

        self.canvas = tk.Canvas(self)


        self.canvas.pack(fill=tk.BOTH, expand=1)

    def create_dot(self,x,y,r,color,label=''):
        self.canvas.create_oval(x-r,y-r,x+r,y+r,outline=color, fill = color)
        self.canvas.create_text(x,y-10,text=label)

    def create_connector(self,xA,yA,xB,yB,angle,color='black'):
        self.create_dot(xA,yA,3,'black')
        self.create_dot(xB,yB,3,'black')
        alpha = math.radians(angle)
        beta = math.atan2((yA-yB),(xB-xA)) # angle between A->B and x-positive
        print('alpha in degrees, ',math.degrees(alpha),'beta in degrees, ',math.degrees(beta))

        # calculate the center of circle

        rad_radiusA = alpha-math.pi*0.5 # radiant of radius of the circle going out from A
        print('rad_radiusA (degrees), ', math.degrees(rad_radiusA),'radians, ',rad_radiusA)
        gA = math.tan(rad_radiusA)
        print('gradiantA, ', gA)
        gAB = (yA-yB)/(xB-xA) # y axis inversed
        print('gradiantAB, ', gAB)

        gM = (-1)/gAB
        print('gradiantM, ',gM)
        xM = (xA+xB)/2
        yM = (yA+yB)/2
        print('M, ',xM,yM)

        xC = (yA+gA*xA-gM*xM-yM)/(gA-gM)
        yC = yA-gA*(xC-xA)
        print("C: ",xC,yC)

        self.create_dot(xC,yC,2,color,str(angle)) # draw center of the circle

        rad_CA = math.atan2((yC-yA),(xA-xC))
        rad_CB = math.atan2((yC-yB),(xB-xC))
        print('radCA, ',rad_CA,'radCB, ',rad_CB)

        diff = rad_CB-rad_CA
        print('diff in degree, ',math.degrees(diff))

        # calculate radius

        radius = (pow((xB-xC),2)+pow((yC-yB),2)) ** 0.5
        baseArc = math.atan2(yC-yA,xA-xC)
        print('baseArc in degrees, ', math.degrees(baseArc))

        # vectors, this part seems to be correct

        vecStarting = [math.cos(alpha),math.sin(alpha)]
        vecAtoB = [xB-xA, yA-yB]
        print('vecStarting, ',vecStarting,'vecAtoB, ',vecAtoB)
        angleCos = self.cosFormula(vecStarting,vecAtoB)
        print('angle in Between, ', angleCos)

        # counter the direction

        inverse = 1
        if angleCos < 0: # you hu
            diff = (math.pi*2 - abs(diff))
            inverse = -1
            print('优弧')
        else:
            print('劣弧')

        # generate new points

        x = [xA]
        y = [yA]
        n = 7

        for i in range(n):
            baseArc += diff/(n+1)
            x1 = xC + radius * math.cos(baseArc)
            x.append(x1)
            y1 = yC - radius * math.sin(baseArc)
            y.append(y1)
            self.create_dot(x1,y1,2,color,str(i))
        x.append(xB)
        y.append(yB)
        self.canvas.create_line(x[0],y[0],x[1],y[1],x[2],y[2],x[3],y[3],x[4],y[4],x[5],y[5],x[6],y[6],x[7],y[7],x[8],y[8],smooth = True,fill= color,arrow= tk.LAST)

        print('\n')

    def cosFormula(self,a,b):
        l = 0
        m = 0
        n = 0
        for i in range(2):
            l += a[i]*b[i]
            m += a[i]**2
            n += b[i]**2
        return l/((m*n)**0.5)
'''
def main():

    root = tk.Tk()
    ex = SFDCanvas()
    root.geometry("1000x1000+900+100")
    root.mainloop()


if __name__=='__main__':
    main()
'''
