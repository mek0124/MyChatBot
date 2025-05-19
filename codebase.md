# .gitignore

```
.env
.venv/
__pycache__/
chat_dataset.db

```

# chat_dataset.db

This is a binary file of the type: Binary

# chat_widget.py

```py
from PySide6 import QtWidgets as qtw
from PySide6 import QtCore as qtc
from PySide6 import QtGui as qtg
from datetime import datetime
import markdown


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


class ChatMessageWidget(qtw.QWidget):
    def __init__(self, message: str, is_user: bool, parent=None):
        super().__init__(parent)
        self.message = message
        self.is_user = is_user
        self.setup_ui()

    def setup_ui(self):
        layout = qtw.QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        self.setLayout(layout)

        sender_label = qtw.QLabel("You" if self.is_user else "Mistral AI")
        sender_label.setAlignment(qtc.Qt.AlignLeft if self.is_user else qtc.Qt.AlignRight)
        sender_label.setStyleSheet(
            """
            font-weight: bold;
            font-size: 12px;
            color: %s;
            margin-bottom: 2px;
            """ % ("rgb(177,203,231)" if self.is_user else "rgb(94,147,207)")
        )
        layout.addWidget(sender_label)

        self.text_edit = qtw.QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setSizePolicy(qtw.QSizePolicy.Expanding, qtw.QSizePolicy.Preferred)
        self.text_edit.setHorizontalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
        self.text_edit.setVerticalScrollBarPolicy(qtc.Qt.ScrollBarAlwaysOff)
        self.text_edit.setStyleSheet(
            f"""
            QTextEdit {{
                background-color: {'rgb(0,38,80)' if self.is_user else 'rgb(0,22,45)'};
                border: 1px solid {'rgb(33,84,141)' if self.is_user else 'rgb(33,84,141)'};
                border-radius: 12px;
                padding: 12px;
                font-size: 14px;
                margin-bottom: 8px;
                color: rgb(177,203,231);
            }}
            """
        )

        if self.message:
            self.set_markdown_content(self.text_edit, self.message)
        layout.addWidget(self.text_edit)

        if self.message:
            self.adjust_height()

        if not self.is_user and self.message:
            button_layout = qtw.QHBoxLayout()
            button_layout.setAlignment(qtc.Qt.AlignRight)
            button_layout.setSpacing(5)
            
            self.copy_button = qtw.QPushButton("Copy")
            self.copy_button.setStyleSheet("""
                QPushButton {
                    padding: 4px 8px;
                    border: 1px solid rgb(33,84,141);
                    border-radius: 4px;
                    background-color: rgb(0,38,80);
                    font-size: 12px;
                    color: rgb(177,203,231);
                }
                QPushButton:hover {
                    background-color: rgb(94,147,207);
                }
            """)
            self.copy_button.clicked.connect(self.copy_markdown)
            button_layout.addWidget(self.copy_button)
            
            self.save_md_button = qtw.QPushButton("Save MD")
            self.save_md_button.setStyleSheet("""
                QPushButton {
                    padding: 4px 8px;
                    border: 1px solid rgb(33,84,141);
                    border-radius: 4px;
                    background-color: rgb(0,38,80);
                    font-size: 12px;
                    color: rgb(177,203,231);
                }
                QPushButton:hover {
                    background-color: rgb(94,147,207);
                }
            """)
            self.save_md_button.clicked.connect(lambda: self.save_markdown('md'))
            button_layout.addWidget(self.save_md_button)
            
            self.save_txt_button = qtw.QPushButton("Save TXT")
            self.save_txt_button.setStyleSheet("""
                QPushButton {
                    padding: 4px 8px;
                    border: 1px solid rgb(33,84,141);
                    border-radius: 4px;
                    background-color: rgb(0,38,80);
                    font-size: 12px;
                    color: rgb(177,203,231);
                }
                QPushButton:hover {
                    background-color: rgb(94,147,207);
                }
            """)
            self.save_txt_button.clicked.connect(lambda: self.save_markdown('txt'))
            button_layout.addWidget(self.save_txt_button)
            
            layout.addLayout(button_layout)

        if not self.is_user and self.message:
            self.text_edit.setContextMenuPolicy(qtc.Qt.CustomContextMenu)
            self.text_edit.customContextMenuRequested.connect(self.show_context_menu)

    def adjust_height(self):
        doc = self.text_edit.document()
        doc.setTextWidth(self.text_edit.viewport().width())
        height = int(doc.size().height()) + 30
        self.text_edit.setMinimumHeight(min(height, 500))
        self.text_edit.setMaximumHeight(min(height, 500))

    def set_markdown_content(self, text_edit: qtw.QTextEdit, markdown_text: str):
        html = markdown.markdown(markdown_text)
        doc = qtg.QTextDocument()
        doc.setHtml(html)
        text_edit.setDocument(doc)
        qtc.QTimer.singleShot(100, self.adjust_height)

    def show_context_menu(self, position):
        menu = qtw.QMenu(self)
        
        copy_action = qtg.QAction("Copy Markdown", self)
        copy_action.triggered.connect(self.copy_markdown)
        menu.addAction(copy_action)
        
        save_md_action = qtg.QAction("Save as Markdown (.md)", self)
        save_md_action.triggered.connect(lambda: self.save_markdown('md'))
        menu.addAction(save_md_action)
        
        save_txt_action = qtg.QAction("Save as Text (.txt)", self)
        save_txt_action.triggered.connect(lambda: self.save_markdown('txt'))
        menu.addAction(save_txt_action)
        
        menu.exec_(self.text_edit.mapToGlobal(position))

    def copy_markdown(self):
        clipboard = qtw.QApplication.clipboard()
        mime_data = qtc.QMimeData()
        mime_data.setText(self.message)
        clipboard.setMimeData(mime_data)
        qtw.QMessageBox.information(self, "Copied", "Markdown content copied to clipboard!")

    def save_markdown(self, extension: str):
        default_name = f"mistral_response_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"
        file_path, _ = qtw.QFileDialog.getSaveFileName(
            self, 
            "Save Markdown Content", 
            default_name, 
            f"Markdown Files (*.{extension});;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.message)
                qtw.QMessageBox.information(self, "Saved", f"Content saved successfully to {file_path}")
            except Exception as e:
                qtw.QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

    def resizeEvent(self, event):
        if self.message:
            self.adjust_height()
        super().resizeEvent(event)
```

# dataset_agent.py

```py
from PySide6 import QtCore as qtc
import sqlite3
import uuid
from typing import Optional


class DatasetAgent:
    def __init__(self):
        self.db_path = "chat_dataset.db"
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used_at TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    sender_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(sender_id) REFERENCES profiles(id)
                )
            """)
            conn.commit()

    def get_or_create_profile(self, entity_type: str) -> str:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id FROM profiles 
                WHERE entity_type = ?
                ORDER BY last_used_at DESC
                LIMIT 1
            """, (entity_type,))
            result = cursor.fetchone()
            
            if result:
                profile_id = result[0]
                cursor.execute("""
                    UPDATE profiles 
                    SET last_used_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (profile_id,))
            else:
                profile_id = str(uuid.uuid4())
                cursor.execute("""
                    INSERT INTO profiles (id, entity_type)
                    VALUES (?, ?)
                """, (profile_id, entity_type))
            
            conn.commit()
            return profile_id

    def log_message(self, conversation_id: str, sender_id: str, content: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (conversation_id, sender_id, content)
                VALUES (?, ?, ?)
            """, (conversation_id, sender_id, content))
            conn.commit()


class DatasetAgentWorker(qtc.QThread):
    profile_ready = qtc.Signal(str)
    logging_complete = qtc.Signal(bool)
    error_occurred = qtc.Signal(str)
    finished_signal = qtc.Signal()

    def __init__(self, entity_type: Optional[str] = None, 
                 conversation_id: Optional[str] = None,
                 sender_id: Optional[str] = None,
                 content: Optional[str] = None,
                 parent=None):
        super().__init__(parent)
        self.entity_type = entity_type
        self.conversation_id = conversation_id
        self.sender_id = sender_id
        self.content = content
        self.mode = 'get_profile' if entity_type else 'log_message'

    def run(self):
        try:
            agent = DatasetAgent()
            if self.mode == 'get_profile':
                profile_id = agent.get_or_create_profile(self.entity_type)
                self.profile_ready.emit(profile_id)
            else:
                agent.log_message(
                    conversation_id=self.conversation_id,
                    sender_id=self.sender_id,
                    content=self.content
                )
                self.logging_complete.emit(True)
        except Exception as e:
            self.error_occurred.emit(f"Dataset error: {str(e)}")
        finally:
            self.finished_signal.emit()
```

# main.py

```py
from PySide6 import QtWidgets as qtw
from PySide6 import QtCore as qtc
from PySide6 import QtGui as qtg
from dotenv import load_dotenv
from pathlib import Path
from chat_widget import ChatMessageWidget, LoadingWidget
from mistral_agent import MistralWorker
from dataset_agent import DatasetAgentWorker
import base64
import uuid

load_dotenv()

class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mistral AI Chat")
        self.setGeometry(100, 100, 800, 600)
        self.conversation_id = str(uuid.uuid4())
        self.user_id = None
        self.ai_id = None
        self.worker_threads = []
        
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
        self.init_profiles()

    def init_profiles(self):
        user_worker = DatasetAgentWorker(entity_type='user')
        user_worker.profile_ready.connect(self.set_user_id)
        user_worker.error_occurred.connect(
            lambda e: print(f"Error getting user profile: {e}"))
        user_worker.finished_signal.connect(self.cleanup_thread)
        self.worker_threads.append(user_worker)
        user_worker.start()
        
        ai_worker = DatasetAgentWorker(entity_type='ai')
        ai_worker.profile_ready.connect(self.set_ai_id)
        ai_worker.error_occurred.connect(
            lambda e: print(f"Error getting AI profile: {e}"))
        ai_worker.finished_signal.connect(self.cleanup_thread)
        self.worker_threads.append(ai_worker)
        ai_worker.start()

    def set_user_id(self, user_id: str):
        self.user_id = user_id
        print(f"User ID set: {user_id}")

    def set_ai_id(self, ai_id: str):
        self.ai_id = ai_id
        print(f"AI ID set: {ai_id}")

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

        self.send_button.clicked.connect(self.send_message)
        self.file_button.clicked.connect(self.attach_file)
        self.image_button.clicked.connect(self.attach_image)

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

    def send_message(self):
        message = self.input_text.toPlainText().strip()
        if not message or not self.user_id or not self.ai_id:
            return
            
        self.add_message(message, is_user=True)
        self.input_text.clear()
        
        self.log_message(message, self.user_id)
        
        self.show_loading_indicator()
        
        self.worker_thread = MistralWorker(message)
        self.worker_thread.response_received.connect(self.handle_response)
        self.worker_thread.error_occurred.connect(self.handle_error)
        self.worker_thread.finished_signal.connect(self.cleanup_thread)
        self.worker_threads.append(self.worker_thread)
        self.worker_thread.start()

    def handle_response(self, response: str):
        self.hide_loading_indicator()
        self.add_message(response, is_user=False)
        self.statusBar().showMessage("Response received", 3000)
        if self.ai_id:
            self.log_message(response, self.ai_id)

    def handle_error(self, error: str):
        self.hide_loading_indicator()
        self.add_message(error, is_user=False)
        self.statusBar().showMessage("Error occurred", 3000)

    def log_message(self, content: str, sender_id: str):
        worker = DatasetAgentWorker(
            conversation_id=self.conversation_id,
            sender_id=sender_id,
            content=content
        )
        worker.logging_complete.connect(
            lambda success: print("Message logged" if success else "Failed to log message"))
        worker.error_occurred.connect(
            lambda error: print(f"Error logging message: {error}"))
        worker.finished_signal.connect(self.cleanup_thread)
        self.worker_threads.append(worker)
        worker.start()

    def cleanup_thread(self):
        self.worker_threads = [t for t in self.worker_threads if t.isRunning()]

    def closeEvent(self, event):
        for thread in self.worker_threads:
            if thread.isRunning():
                thread.quit()
                thread.wait()
        event.accept()

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
```

# mistral_agent.py

```py
from PySide6 import QtCore as qtc
from mistralai import Mistral
import os


class MistralWorker(qtc.QThread):
    response_received = qtc.Signal(str)
    error_occurred = qtc.Signal(str)
    finished_signal = qtc.Signal()

    def __init__(self, prompt: str, parent=None):
        super().__init__(parent)
        self.prompt = prompt

    def run(self):
        try:
            api_key = os.environ.get("MISTRAL_API_KEY")
            
            if not api_key:
                self.error_occurred.emit("Error: MISTRAL_API_KEY not found in environment variables.")
                return

            model = "mistral-large-latest"
            client = Mistral(api_key=api_key)

            messages = [{"role": "user", "content": self.prompt}]

            chat_response = client.chat.complete(
                model=model,
                messages=messages,
            )
            self.response_received.emit(chat_response.choices[0].message.content)
        except Exception as e:
            self.error_occurred.emit(f"An error occurred: {e}")
        finally:
            self.finished_signal.emit()
```

# requirements.txt

```txt
annotated-types==0.7.0
anyio==4.9.0
certifi==2025.4.26
eval-type-backport==0.2.2
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
idna==3.10
markdown==3.8
mistralai==1.7.0
pip==25.1.1
pydantic==2.11.4
pydantic-core==2.33.2
pyside6==6.9.0
pyside6-addons==6.9.0
pyside6-essentials==6.9.0
python-dateutil==2.9.0.post0
python-dotenv==1.1.0
shiboken6==6.9.0
six==1.17.0
sniffio==1.3.1
typing-extensions==4.13.2
typing-inspection==0.4.0
uv==0.7.5
uvloop==0.21.0
```

