from PySide6 import QtWidgets as qtw
from dotenv import load_dotenv
from frontend.views.main_window import MainWindow
from frontend.controllers.main_controller import MainController

load_dotenv()

def main():
    app = qtw.QApplication([])
    
    controller = MainController()
    window = MainWindow(controller)
    
    # Connect controller to view
    controller.response_received = window.add_message
    controller.error_occurred = window.add_message
    controller.show_loading = window.show_loading_indicator
    controller.hide_loading = window.hide_loading_indicator
    controller.clear_input = window.clear_input
    controller.show_status = window.show_status_message
    
    window.show()
    app.exec()

if __name__ == "__main__":
    main()