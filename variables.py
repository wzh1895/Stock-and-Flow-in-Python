from xml.dom.minidom import parse
import xml.dom.minidom
 
# open XML file with minidom
DOMTree = xml.dom.minidom.parse("ReindeerModel.stmx")
model = DOMTree.documentElement

# fetch all variables in the file
# since there is only one "variables" in the file, the outcome
# is a list containing only one element of "variables"
allvariables = model.getElementsByTagName("variables")

# fetch all stocks in all variables (the only element in the list)
stock_defs = allvariables[0].getElementsByTagName("stock")
 
# print details of every stock
for stock in stock_defs:
   print("\n*****Stock*****")
   #if stock.hasAttribute("name"):
   print("Name: %s" % stock.getAttribute("name"))
   inflow = stock.getElementsByTagName('inflow')[0]
   print("Inflow: %s" % inflow.childNodes[0].data)
   outflow = stock.getElementsByTagName('outflow')[0]
   print("Outflow: %s" % outflow.childNodes[0].data)
   eqn = stock.getElementsByTagName('eqn')[0]
   print("Equation: %s" % eqn.childNodes[0].data)

# fetch all flows
flow_defs = allvariables[0].getElementsByTagName("flow")

# print details of every flow
for flow in flow_defs:
   print("\n*****Flow*****")
   print("Name: %s" % flow.getAttribute("name"))
   eqn = flow.getElementsByTagName("eqn")[0]
   print("Equation: %s" % eqn.childNodes[0].data)

# fetch all auxiliaries
aux_defs = allvariables[0].getElementsByTagName("aux")

# print details of every aux
for aux in aux_defs:
   print("\n*****Auxiliary*****")
   print("Name: %s" % aux.getAttribute("name"))
   eqn = aux.getElementsByTagName("eqn")[0]
   print("Equation: %s" % eqn.childNodes[0].data)


#=====================================================#


# fetch all views in the file ---> down to the view
allviews = model.getElementsByTagName("views")
views = allviews[0].getElementsByTagName("view")

# fetch views for all stocks
stockviews = []
for stockview in views[0].getElementsByTagName("stock"):
   if stockview.hasAttribute("name"):
      stockviews.append(stockview)

for stockview in stockviews:
   print("\n*****Stock View*****")
   print("Name: %s" % stockview.getAttribute("name"))
   print("x: %s" % stockview.getAttribute("x"))
   print("y: %s" % stockview.getAttribute("y"))

# fetch views for all flows
flowviews = []
for flowview in views[0].getElementsByTagName("flow"):
   if flowview.hasAttribute("name"):
      flowviews.append(flowview)

for flowview in flowviews:
   print("\n*****Flow View*****")
   print("Name: %s" % flowview.getAttribute("name"))
   print("x: %s" % flowview.getAttribute("x"))
   print("y: %s" % flowview.getAttribute("y"))
   points = flowview.getElementsByTagName("pt")
   for point in points:
      print("    *****Point*****")
      print("    x: %s" % point.getAttribute("x"))
      print("    y: %s" % point.getAttribute("y"))

# fetch views for all connectors
connectorviews = []
for connectorview in views[0].getElementsByTagName("connector"):
   if connectorview.hasAttribute("uid"):
      connectorviews.append(connectorview)

for connectorview in connectorviews:
   print("\n*****Connector View*****")
   print("uid: %s" % connectorview.getAttribute("uid"))
   print("angle: %s" % connectorview.getAttribute("angle"))
   from_var = connectorview.getElementsByTagName("from")[0]
   print("From: %s" % from_var.childNodes[0].data)
   to_var = connectorview.getElementsByTagName("to")[0]
   print("To: %s" % to_var.childNodes[0].data)

# fetch views for all auxiliaries
auxviews = []
for auxview in views[0].getElementsByTagName("aux"):
   if auxview.hasAttribute("name"):
      auxviews.append(auxview)

for auxview in auxviews:
   print("\n*****Auxiliary View*****")
   print("Name: %s" % auxview.getAttribute("name"))
   print("x: %s" % auxview.getAttribute("x"))
   print("y: %s" % auxview.getAttribute("y"))


print("\n")