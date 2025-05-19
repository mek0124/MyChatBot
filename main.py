from PySide6 import QtWidgets as qtw
from dotenv import load_dotenv
from frontend.views.main_window import MainWindow
from frontend.controllers.main_controller import MainController

load_dotenv()

def main():
    app = qtw.QApplication([])
    
    controller = MainController()
    window = MainWindow(controller)
    
    # Connect controller signals to view methods
    controller.display_user_message.connect(
        lambda msg: window.add_message(msg, is_user=True))
    controller.display_ai_message.connect(
        lambda msg: window.add_message(msg, is_user=False))
    controller.show_loading.connect(window.show_loading_indicator)
    controller.hide_loading.connect(window.hide_loading_indicator)
    controller.error_occurred.connect(
        lambda error: window.add_message(error, is_user=False))
    
    window.show()
    app.exec()

if __name__ == "__main__":
    main()