class Stock():
    def __init__(self, name, x, y, eqn = "none", inflow = "none", outflow = "none"):    
        self.name = name
        self.eqn = eqn
        self.x = float(x)
        self.y = float(y)
        self.inflow = inflow
        self.outflow = outflow

class Flow():
    def __init__(self, name, x, y, xA, yA, xB, yB, eqn = "none"):
        self.name = name
        self.eqn = eqn
        self.x = float(x)
        self.y = float(y)
        self.xA = float(xA)
        self.yA = float(yA)
        self.xB = float(xB)
        self.yB = float(yB)

class Aux():
    def __init__(self, name, x, y, eqn = "none"):
        self.name = name
        self.eqn = eqn
        self.x = float(x)
        self.y = float(y)

class Connector():
    def __init__(self, uid, angle, from_var, to_var):
        self.uid = uid
        self.angle = float(angle)
        self.from_var = from_var
        self.to_var = to_var

class Alias():
    def __init__(self, uid, x, y, of):
        self.uid = uid
        self.x = float(x)
        self.y = float(y)
        self.of = of