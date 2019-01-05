import globalModel


class Element():
    def __init__(self, name, x, y, eqn="none"):
        self.name = name
        self.eqn = eqn
        self.x = float(x)
        self.y = float(y)
        self.value = None
        self.behavior = []


class Stock(Element):
    def __init__(self, name, x, y, eqn = "none", inflow = "none", outflow = "none"):    
        super(Stock, self).__init__(name, x, y, eqn)
        self.inflow = inflow
        self.outflow = outflow
        try:
            self.value = float(self.eqn)
        except ValueError:
            exec('self.value='+self.eqn)
        self.behavior.append(self.value)

    def __call__(self):
        return self.value

    def change_in_stock(self, amount):
        self.value += amount
        self.behavior.append(self.value)


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


class Time():
    def __init__(self, end, start=1, dt=0.125):
        self.start = start
        self.end = end
        self.dt = dt
        self.steps = int((self.end-self.start)/self.dt)
        self.current_step = 1
