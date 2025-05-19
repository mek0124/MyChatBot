from PySide6 import QtWidgets as qtw
from PySide6 import QtCore as qtc
from PySide6 import QtGui as qtg

class LoadingWidget(qtw.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.start_animation()

    def setup_ui(self):
        layout = qtw.QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(qtc.Qt.AlignLeft)
        self.setLayout(layout)

        self.loading_label = qtw.QLabel("Mistral AI is thinking...")
        self.loading_label.setStyleSheet("""
            color: rgb(94,147,207);
            font-style: italic;
            font-size: 14px;
        """)
        layout.addWidget(self.loading_label)

        self.spinner = qtw.QLabel()
        self.spinner_movie = qtg.QMovie(":loading.gif")
        self.spinner.setMovie(self.spinner_movie)
        layout.addWidget(self.spinner)

    def start_animation(self):
        self.spinner_movie.start()

    def stop_animation(self):
        self.spinner_movie.stop()
        self.hide()