from StockAndFlowInPython.graph_sd.graph_engine import *


def main():
    structure_0 = Structure()
    print("\nSystem Dynamics Console in Python\n"
          "Author: wzh1895@outlook.com\n")

    def menu_main():
        selection = input("Select an action:\n\n"
                          "1: Add\n"
                          "2: Select\n"
                          "3: Delete\n"
                          "4: Simulate\n"
                          "5: Display\n"
                          "6: Graph\n"
                          "0: Quit\n")
        return selection

    def menu_type_to_add():
        type_to_add = input("Add a what?\n\n"
                            "s: Stock\n"
                            "f: Flow\n"
                            "a: Auxiliary\n")
        return type_to_add

    if_continue = True
    while if_continue:
        selection = menu_main()
        if selection == '1':
            type_to_add = menu_type_to_add()
            if type_to_add == 's':
                n = input("Name:")
                e = input("Equation:")
                structure_0.add_stock(name=n, equation=[float(e)])
                structure_0.print_elements()
                structure_0.print_causal_links()
            elif type_to_add == 'f':
                pass
            elif type_to_add == 'a':
                pass
            else:
                print("Invalid input.")
        elif selection == '2':
            pass
        elif selection == '3':
            pass
        elif selection == '4':
            t = input("For how long?")
            if t != '':
                try:
                    t = int(t)
                except ValueError:
                    print('Invalid time input.')
                    t = ''
            dt = input("Time step?")
            if dt != '':
                try:
                    dt = int(dt)
                except ValueError:
                    print('Invalid time step input.')
                    dt = ''
            structure_0.simulate(simulation_time=t if t != '' else 25,
                                 dt=dt if dt != '' else 0.25)
        elif selection == '5':
            structure_0.print_elements()
            structure_0.print_causal_links()
        elif selection == '6':
            pass
        elif selection == '0':
            print('Quit.')
            if_continue = False
        else:
            print('Invalid input.')


if __name__ == '__main__':
    main()
