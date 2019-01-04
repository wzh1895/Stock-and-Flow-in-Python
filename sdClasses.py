import globalElements


class Element():
    def __init__(self, name, x, y, eqn="none"):
        self.name = name
        self.eqn = eqn
        self.x = float(x)
        self.y = float(y)
        self.value = None


class Stock(Element):
    def __init__(self, name, x, y, eqn = "none", inflow = "none", outflow = "none"):    
        super(Stock, self).__init__(name, x, y, eqn)
        self.inflow = inflow
        self.outflow = outflow
        self.value = float(self.eqn)

    def __call__(self):
        return self.value

    def change_in_stock(self, amount):
        self.value += amount


class Flow(Element):
    def __init__(self, name, x, y, pts, eqn = "none"):
        super(Flow, self).__init__(name, x, y, eqn)
        self.pts = pts

    def __call__(self):
        try:
            self.value = float(self.eqn)
            return self.value
        except ValueError:
            exec('self.value='+self.eqn)
            return self.value


class Aux(Element):
    def __init__(self, name, x, y, eqn = "none"):
        super(Aux, self).__init__(name, x, y, eqn)

    def __call__(self):
        try:
            self.value = float(self.eqn)
            return self.value
        except ValueError:
            exec('self.value='+self.eqn)
            return self.value

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
