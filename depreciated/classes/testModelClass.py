from depreciated.classes import Model

md = Model()

print(md)

md.add_stock(name='stock1', x=289, y=145, eqn=str(100), inflow='flow1')
md.add_flow(name='flow1', x=181.75, y=145, pts=[(85, 145), (266.5, 145)],
            eqn="(get_value('goal1')()-get_value('stock1')())/get_value('at1')()")
md.add_aux(name='at1', x=141.5, y=56.5, eqn=str(5))
md.add_aux(name='goal1', x=148, y=229, eqn=str(1))
md.set_timer(name='time1', start=1, end=25, dt=0.125)
md.add_connector(150, from_var='stock1', to_var='flow1')
md.add_connector(200, from_var='at1', to_var='flow1')
md.add_connector(60, from_var='goal1', to_var='flow1')
md.add_connector(1, from_var='flow1', to_var='stock1')


#md.print_all_variables()
md.print_all_connectors()
#md.draw_cld()

#print(md.get_var_by_name('stock1'))


# md.run()
