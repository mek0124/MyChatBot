from PySide6 import QtWidgets as qtw
from PySide6 import QtCore as qtc

from dotenv import load_dotenv
from pathlib import Path

from chat_widget import ChatMessageWidget, LoadingWidget
from mistral_agent import MistralWorker

import base64

load_dotenv()

class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mistral AI Chat")
        self.setGeometry(100, 100, 800, 600)
        
        # Set application-wide stylesheet with new theme
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
        
        self.setup_ui()
        self.worker_thread = None
        self.loading_widget = None

    def setup_ui(self):
        central_widget = qtw.QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = qtw.QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        central_widget.setLayout(main_layout)

        # Chat history area
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

        # Input area
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

        # Button layout
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

        # Add status bar
        self.statusBar().setStyleSheet("""
            QStatusBar {
                background-color: rgb(0,38,80);
                color: rgb(177,203,231);
                font-size: 12px;
                padding: 4px;
                border-top: 1px solid rgb(33,84,141);
            }
        """)

        # Connect signals
        self.send_button.clicked.connect(self.send_message)
        self.file_button.clicked.connect(self.attach_file)
        self.image_button.clicked.connect(self.attach_image)

    def add_message(self, message: str, is_user: bool):
        message_widget = ChatMessageWidget(message, is_user)
        self.chat_layout.addWidget(message_widget)
        
        # Add fade-in animation
        animation = qtc.QPropertyAnimation(message_widget, b"windowOpacity")
        animation.setDuration(300)
        animation.setStartValue(0)
        animation.setEndValue(1)
        animation.start()
        
        # Scroll to bottom
        qtc.QTimer.singleShot(100, self.scroll_to_bottom)
        return message_widget

    def show_loading_indicator(self):
        """Show loading animation while waiting for response"""
        if self.loading_widget is None:
            self.loading_widget = LoadingWidget()
            self.chat_layout.addWidget(self.loading_widget)
            qtc.QTimer.singleShot(100, self.scroll_to_bottom)

    def hide_loading_indicator(self):
        """Hide loading animation when response is received"""
        if self.loading_widget:
            self.loading_widget.hide()
            self.loading_widget.deleteLater()
            self.loading_widget = None

    def scroll_to_bottom(self):
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def send_message(self):
        message = self.input_text.toPlainText().strip()
        if not message:
            return
            
        self.add_message(message, is_user=True)
        self.input_text.clear()
        
        # Show loading indicator
        self.show_loading_indicator()
        
        # Start worker thread
        self.worker_thread = MistralWorker(message)
        self.worker_thread.response_received.connect(self.handle_response)
        self.worker_thread.error_occurred.connect(self.handle_error)
        self.worker_thread.start()

    def handle_response(self, response: str):
        # Hide loading indicator
        self.hide_loading_indicator()
        
        # Show response
        self.add_message(response, is_user=False)
        self.statusBar().showMessage("Response received", 3000)

    def handle_error(self, error: str):
        # Hide loading indicator
        self.hide_loading_indicator()
        
        # Show error
        self.add_message(error, is_user=False)
        self.statusBar().showMessage("Error occurred", 3000)

    def attach_file(self):
        file_path, _ = qtw.QFileDialog.getOpenFileName(
            self, "Select File", "", "All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    filename = Path(file_path).name
                    prompt = f"Here is the content of file '{filename}':\n\n{content}\n\nPlease analyze this file."
                    self.add_message(f"Attached file: {filename}", is_user=True)
                    self.input_text.setPlainText(prompt)
            except Exception as e:
                self.add_message(f"Error reading file: {str(e)}", is_user=True)

    def attach_image(self):
        image_path, _ = qtw.QFileDialog.getOpenFileName(
            self, "Select Image", "", "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if image_path:
            try:
                # Read image as base64
                with open(image_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                
                filename = Path(image_path).name
                prompt = f"Here is an image named '{filename}' (base64 encoded):\n\n{encoded_string}\n\nPlease analyze this image."
                self.add_message(f"Attached image: {filename}", is_user=True)
                self.input_text.setPlainText(prompt)
            except Exception as e:
                self.add_message(f"Error processing image: {str(e)}", is_user=True)

if __name__ == "__main__":
    app = qtw.QApplication([])
    
    window = MainWindow()
    window.show()
    
    app.exec()