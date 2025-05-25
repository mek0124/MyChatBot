from PySide6 import QtWidgets as qtw
from dotenv import load_dotenv
from frontend.views.main_window import MainWindow
from frontend.controllers.main_controller import MainController
from pathlib import Path

env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)


def main():
    app = qtw.QApplication([])

    controller = MainController()
    window = MainWindow(controller)

    # Connect controller signals to view methods
    controller.display_user_message.connect(
        lambda msg, attachments=None: window.add_message(
            msg, is_user=True, attachments=attachments
        )
    )
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
