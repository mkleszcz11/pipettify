#################
### MAIN APP ####
#################

from pipettify.controllers.controller_printer import PrinterController
from pipettify.controllers.controller_bed import BedController
from pipettify.gui.gui_main import PrinterGUI
from pipettify.sequence_control.sequence_state_machine import PipettifyStateMachine

import time

def main():
    printer = PrinterController()
    # printer.configure_serial_connection()

    bed_controller = printer.bed_controller
    
    # printer.tool_controller.press_push_button()
    
    
    time.sleep(2)
    # printer.tool_controller._get_absolute_motor_position()

    state_machine = PipettifyStateMachine(printer_controller = printer,
                                          pipette_controller = printer.tool_controller,
                                          bed_controller = bed_controller)
    
    app = PrinterGUI(printer_controller = printer,
                     bed_controller = bed_controller,
                     state_machine = state_machine)

    app.mainloop()

if __name__ == "__main__":
    main()
