from PySide6 import QtWidgets as qtw
from PySide6 import QtCore as qtc
from PySide6 import Qt

from dotenv import load_dotenv
from pathlib import Path

from chat_widget import ChatMessageWidget
from agent import MistralWorker

import base64

load_dotenv()
class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mistral AI Chat")
        self.setGeometry(100, 100, 800, 600)
        
        self.setup_ui()
        self.worker_thread = None

    def setup_ui(self):
        central_widget = qtw.QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = qtw.QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Chat history area
        self.scroll_area = qtw.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.chat_container = qtw.QWidget()
        self.chat_layout = qtw.QVBoxLayout()
        self.chat_layout.setAlignment(Qt.AlignTop)
        self.chat_container.setLayout(self.chat_layout)
        
        self.scroll_area.setWidget(self.chat_container)
        main_layout.addWidget(self.scroll_area)

        # Input area
        input_layout = qtw.QVBoxLayout()
        
        self.input_text = qtw.QTextEdit()
        self.input_text.setPlaceholderText("Type your message here...")
        self.input_text.setMaximumHeight(100)
        input_layout.addWidget(self.input_text)

        # Button layout
        button_layout = qtw.QHBoxLayout()
        
        self.send_button = qtw.QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)
        button_layout.addWidget(self.send_button)

        self.file_button = qtw.QPushButton("Attach File")
        self.file_button.clicked.connect(self.attach_file)
        button_layout.addWidget(self.file_button)

        self.image_button = qtw.QPushButton("Attach Image")
        self.image_button.clicked.connect(self.attach_image)
        button_layout.addWidget(self.image_button)

        input_layout.addLayout(button_layout)
        main_layout.addLayout(input_layout)

    def add_message(self, message: str, is_user: bool):
        message_widget = ChatMessageWidget(message, is_user)
        self.chat_layout.addWidget(message_widget)
        
        # Scroll to bottom
        qtc.QTimer.singleShot(100, self.scroll_to_bottom)

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
        
        # Start worker thread
        self.worker_thread = MistralWorker(message)
        self.worker_thread.response_received.connect(self.handle_response)
        self.worker_thread.error_occurred.connect(self.handle_error)
        self.worker_thread.start()

    def handle_response(self, response: str):
        self.add_message(response, is_user=False)

    def handle_error(self, error: str):
        self.add_message(error, is_user=False)

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
