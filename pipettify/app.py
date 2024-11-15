#################
### MAIN APP ####
#################

# This is the main app, it should run the gui in some sort of the loop, then gui should call some
# functions from the Controller class and end effector class. We could implement some high level
# layer called something like "Behaviour Planner"



# It is just a test for now, no GUI used

from PrinterController import PrinterController

def main():
    printer = PrinterController()

    printer.configure_serial_connection()
    printer.print_current_coordinates()
    
    goal_x, goal_y, goal_z = 20, 20, 20
    printer.move_to_coordinates(goal_x, goal_y, goal_z)
    
    
if __name__ == "__main__":
    main()






