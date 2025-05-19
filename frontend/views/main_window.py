from PySide6 import QtWidgets as qtw
from PySide6 import QtCore as qtc
from ..components.chat_message import ChatMessageWidget
from ..components.loading_widget import LoadingWidget

class MainWindow(qtw.QMainWindow):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.setWindowTitle("Mistral AI Chat")
        self.setGeometry(100, 100, 800, 600)
        self.worker_threads = []
        self.loading_widget = None
        
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        central_widget = qtw.QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = qtw.QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        central_widget.setLayout(main_layout)

        self.scroll_area = qtw.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            background-color: rgb(0,38,80);
            border-radius: 8px;
            border: 1px solid rgb(33,84,141);
        """)
        
        self.chat_container = qtw.QWidget()
        self.chat_layout = qtw.QVBoxLayout()
        self.chat_layout.setAlignment(qtc.Qt.AlignTop)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_layout.setSpacing(15)
        self.chat_container.setLayout(self.chat_layout)
        
        self.scroll_area.setWidget(self.chat_container)
        main_layout.addWidget(self.scroll_area)

        input_layout = qtw.QVBoxLayout()
        input_layout.setContentsMargins(0, 10, 0, 0)
        
        self.input_text = qtw.QTextEdit()
        self.input_text.setPlaceholderText("Type your message here...")
        self.input_text.setMaximumHeight(100)
        self.input_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid rgb(33,84,141);
                border-radius: 12px;
                padding: 12px;
                font-size: 14px;
                background-color: rgb(0,38,80);
                color: rgb(177,203,231);
            }
            QTextEdit:focus {
                border: 2px solid rgb(94,147,207);
            }
        """)
        input_layout.addWidget(self.input_text)

        button_layout = qtw.QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.send_button = qtw.QPushButton("Send")
        button_layout.addWidget(self.send_button)

        self.file_button = qtw.QPushButton("Attach File")
        button_layout.addWidget(self.file_button)

        self.image_button = qtw.QPushButton("Attach Image")
        button_layout.addWidget(self.image_button)

        input_layout.addLayout(button_layout)
        main_layout.addLayout(input_layout)

        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: rgb(0,38,80);
                color: rgb(177,203,231);
                font-size: 12px;
                padding: 4px;
                border-top: 1px solid rgb(33,84,141);
            }
        """)

        self.send_button.clicked.connect(self.on_send_clicked)
        self.file_button.clicked.connect(self.on_attach_file)
        self.image_button.clicked.connect(self.on_attach_image)

    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: rgb(0,22,45);
            }
            QScrollArea {
                border: none;
                background-color: rgb(0,38,80);
            }
            QTextEdit, QTextEdit:focus {
                border: 1px solid rgb(33,84,141);
                border-radius: 8px;
                padding: 8px;
                background-color: rgb(0,38,80);
                color: rgb(177,203,231);
                font-size: 14px;
                selection-background-color: rgb(33,84,141);
                selection-color: rgb(177,203,231);
            }
            QPushButton {
                background-color: rgb(33,84,141);
                color: rgb(177,203,231);
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgb(94,147,207);
            }
            QPushButton:pressed {
                background-color: rgb(33,84,141);
            }
            QMenu {
                background-color: rgb(0,38,80);
                border: 1px solid rgb(33,84,141);
                color: rgb(177,203,231);
            }
            QMenu::item:selected {
                background-color: rgb(94,147,207);
            }
            QMessageBox {
                background-color: rgb(0,38,80);
            }
            QMessageBox QLabel {
                color: rgb(177,203,231);
            }
        """)

    def on_send_clicked(self):
        message = self.input_text.toPlainText().strip()
        if message:
            self.controller.send_message(message)
            self.input_text.clear()

    def on_attach_file(self):
        file_path, _ = qtw.QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*)"
        )
        
        if file_path:
            self.controller.attach_file(file_path)

    def on_attach_image(self):
        image_path, _ = qtw.QFileDialog.getOpenFileName(
            self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if image_path:
            self.controller.attach_image(image_path)

    def add_message(self, message: str, is_user: bool):
        message_widget = ChatMessageWidget(message, is_user)
        self.chat_layout.addWidget(message_widget)
        
        animation = qtc.QPropertyAnimation(message_widget, b"windowOpacity")
        animation.setDuration(300)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.start()
        
        qtc.QTimer.singleShot(100, self.scroll_to_bottom)
        return message_widget

    def show_loading_indicator(self):
        if self.loading_widget is None:
            self.loading_widget = LoadingWidget()
            self.chat_layout.addWidget(self.loading_widget)
            qtc.QTimer.singleShot(100, self.scroll_to_bottom)

    def hide_loading_indicator(self):
        if self.loading_widget:
            self.loading_widget.hide()
            self.loading_widget.deleteLater()
            self.loading_widget = None

    def scroll_to_bottom(self):
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def clear_input(self):
        self.input_text.clear()

    def show_status_message(self, message: str, timeout: int = 3000):
        self.statusBar().showMessage(message, timeout)

    def closeEvent(self, event):
        for thread in self.worker_threads:
            if thread.isRunning():
                thread.quit()
                thread.wait()
        event.accept()