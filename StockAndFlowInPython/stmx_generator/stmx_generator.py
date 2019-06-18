import xml.dom.minidom


def read_stmx(filename):
    file = xml.dom.minidom.parse(filename)
    # root = stmx_file.documentElement
    return file

def add_unit(where,name,alias1,alias2):
    # First create a standalone unit node, build its inner structure
    new_node = where.createElement("unit")
    new_node.setAttribute("name",name)
    new_node.appendChild(where.createElement("eqn"))
    new_node.appendChild(where.createElement("alias"))
    new_node.childNodes[1].appendChild(where.createTextNode(alias1))
    new_node.appendChild(where.createElement("alias"))
    new_node.childNodes[2].appendChild(where.createTextNode(alias2))

    # Then confirm it to: root/xmile/model_units
    where.getElementsByTagName("xmile")[0].getElementsByTagName("model_units")[0].appendChild(new_node)


def add_stock(where,name,eqn=None,inflow=None,outflow=None,units=None):
    new_node = where.createElement("stock")
    new_node.setAttribute("name",name)
    if eqn != None:
        eqn_node = new_node.appendChild(where.createElement("eqn"))
        eqn_node.appendChild(where.createTextNode(eqn))
    if inflow != None:
        inflow_node = new_node.appendChild(where.createElement("inflow"))
        inflow_node.appendChild(where.createTextNode(inflow))
    if outflow != None:
        outflow_node = new_node.appendChild(where.createElement("outflow"))
        outflow_node.appendChild(where.createTextNode(outflow))
    if units != None:
        units_node = new_node.appendChild(where.createElement("units"))
        units_node.appendChild(where.createTextNode(units))
    where.getElementsByTagName("xmile")[0].getElementsByTagName("model")[0].getElementsByTagName("variables")[0].appendChild(new_node)


def add_flow(where,name,eqn=None,units=None):
    new_node = where.createElement("flow")
    new_node.setAttribute("name", name)
    if eqn != None:
        eqn_node = new_node.appendChild(where.createElement("eqn"))
        eqn_node.appendChild(where.createTextNode(eqn))
    if units != None:
        units_node = new_node.appendChild(where.createElement("units"))
        units_node.appendChild(where.createTextNode(units))
    where.getElementsByTagName("xmile")[0].getElementsByTagName("model")[0].getElementsByTagName("variables")[
        0].appendChild(new_node)


def add_aux(where,name,eqn=None,units=None):
    new_node = where.createElement("aux")
    new_node.setAttribute("name",name)
    if eqn != None:
        eqn_node = new_node.appendChild(where.createElement("eqn"))
        eqn_node.appendChild(where.createTextNode(eqn))
    if units != None:
        units_node = new_node.appendChild(where.createElement("units"))
        units_node.appendChild(where.createTextNode(units))
    where.getElementsByTagName("xmile")[0].getElementsByTagName("model")[0].getElementsByTagName("variables")[
        0].appendChild(new_node)


def add_dependency(where,to_var,from_var):
    # if target var doesn't exist, create it
    if where.getElementsByTagName("xmile")[0].getElementsByTagName("model")[0].getElementsByTagName("variables")[0].getElementsByTagName("isee:dependencies")[0].getElementsByTagName("var") == []:
        var_node = where.createElement("var")
        var_node.setAttribute("name",to_var)
        where.getElementsByTagName("xmile")[0].getElementsByTagName("model")[0].getElementsByTagName("variables")[
            0].getElementsByTagName("isee:dependencies")[0].appendChild(var_node)
    in_node = where.createElement("in")
    in_node.appendChild(where.createTextNode(from_var))
    where.getElementsByTagName("xmile")[0].getElementsByTagName("model")[0].getElementsByTagName("variables")[
        0].getElementsByTagName("isee:dependencies")[0].getElementsByTagName("var")[0].appendChild(in_node)


def add_stock_view(where,x,y,name):
    "xmile/model/views/view"
    stock_view_node = where.createElement("stock")
    stock_view_node.setAttribute("x",str(x))
    stock_view_node.setAttribute("y",str(y))
    stock_view_node.setAttribute("name",name)
    where.getElementsByTagName("xmile")[0].getElementsByTagName("model")[0].getElementsByTagName("views")[0].getElementsByTagName("view")[0].appendChild(stock_view_node)


def add_flow_view(where,x,y,points,name):
    flow_view_node = where.createElement("flow")
    flow_view_node.setAttribute("x",str(x))
    flow_view_node.setAttribute("y",str(y))
    flow_view_node.setAttribute("name",name)
    pts_node = where.createElement("pts")

    def add_point_view(x,y):
        pt_node = where.createElement("pt")
        pt_node.setAttribute("x",str(x))
        pt_node.setAttribute("y",str(y))
        pts_node.appendChild(pt_node)

    for point in points:
        add_point_view(point[0],point[1])

    flow_view_node.appendChild(pts_node)
    where.getElementsByTagName("xmile")[0].getElementsByTagName("model")[0].getElementsByTagName("views")[
        0].getElementsByTagName("view")[0].appendChild(flow_view_node)


def add_aux_view(where,x,y,name):
    aux_view_node = where.createElement("aux")
    aux_view_node.setAttribute("x",str(x))
    aux_view_node.setAttribute("y",str(y))
    aux_view_node.setAttribute("name", name)
    where.getElementsByTagName("xmile")[0].getElementsByTagName("model")[0].getElementsByTagName("views")[
        0].getElementsByTagName("view")[0].appendChild(aux_view_node)


def add_connector_view(where,uid,angle,from_var,to_var):
    connector_view_node = where.createElement("connector")
    connector_view_node.setAttribute("uid",str(uid))
    connector_view_node.setAttribute("angle",str(angle))
    from_node = where.createElement("from")
    from_node.appendChild(where.createTextNode(from_var))
    connector_view_node.appendChild(from_node)
    to_node = where.createElement("to")
    to_node.appendChild(where.createTextNode(to_var))
    connector_view_node.appendChild(to_node)
    where.getElementsByTagName("xmile")[0].getElementsByTagName("model")[0].getElementsByTagName("views")[
        0].getElementsByTagName("view")[0].appendChild(connector_view_node)


def write_stmx(tree,filename):
    file_handle = open(filename, 'w')
    tree.writexml(file_handle, '', '', '', 'UTF-8')
    file_handle.close()


stmx_file = read_stmx('blank_stmx.stmx')  # read a blank .stmx file as template

add_unit(stmx_file,name="Months",alias1="mo",alias2="month")
add_stock(stmx_file,name="Temperature",eqn="100",inflow="Change_in_Temperature",units="C")
add_flow(stmx_file,name="Change in Temperature",eqn="(Goal-Temperature)/Adjustment_Time",units="C/Months")
add_aux(stmx_file,name="Adjustment Time",eqn="5",units="Months")
add_aux(stmx_file,name="Goal",eqn="20",units="C")
add_dependency(stmx_file,to_var="Change_in_Temperature",from_var="Temperature")
add_dependency(stmx_file,to_var="Change_in_Temperature",from_var="Adjustment_Time")
add_dependency(stmx_file,to_var="Change_in_Temperature",from_var="Goal")
add_stock_view(stmx_file,379,260,"Temperature")
add_flow_view(stmx_file,x=271.75,y=260,points=[(175,260),(356.5,260)],name="Change in Temperature")
add_aux_view(stmx_file,227,149,"Adjustment Time")
add_aux_view(stmx_file,238,344,"Goal")
add_connector_view(stmx_file,1,116.565,"Temperature","Change_in_Temperature")
add_connector_view(stmx_file,2,306.87,"Adjustment_Time","Change_in_Temperature")
add_connector_view(stmx_file,3,60.9454,"Goal","Change_in_Temperature")

write_stmx(stmx_file,"out.stmx")

#print(stmx_file.toxml())
