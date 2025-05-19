# .dockerignore

```
.git
.gitignore
.venv
__pycache__
*.db
*.pyc
*.pyo
*.pyd
.DS_Store
codebase.md
.env.template
```

# backend/agents/dataset_agent.py

```py
import sqlite3
import uuid
import os
from typing import Optional
from PySide6 import QtCore as qtc
from ..models.message import Message
from ..models.profile import Profile

class DatasetAgent:
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(backend_dir, "chat_dataset.db")
        else:
            self.db_path = db_path
            
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
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

    def get_or_create_profile(self, entity_type: str) -> Profile:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, created_at, last_used_at FROM profiles 
                WHERE entity_type = ?
                ORDER BY last_used_at DESC
                LIMIT 1
            """, (entity_type,))
            result = cursor.fetchone()
            
            if result:
                profile = Profile(
                    id=result[0],
                    entity_type=entity_type,
                    created_at=result[1],
                    last_used_at=result[2]
                )
                cursor.execute("""
                    UPDATE profiles 
                    SET last_used_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (profile.id,))
            else:
                profile = Profile(
                    id=str(uuid.uuid4()),
                    entity_type=entity_type
                )
                cursor.execute("""
                    INSERT INTO profiles (id, entity_type)
                    VALUES (?, ?)
                """, (profile.id, profile.entity_type))
            
            conn.commit()
            return profile

    def log_message(self, message: Message):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO messages (conversation_id, sender_id, content)
                VALUES (?, ?, ?)
            """, (message.conversation_id, message.sender_id, message.content))
            conn.commit()

class DatasetAgentWorker(qtc.QThread):
    profile_ready = qtc.Signal(Profile)
    logging_complete = qtc.Signal(bool)
    error_occurred = qtc.Signal(str)
    finished_signal = qtc.Signal()

    def __init__(self, entity_type: Optional[str] = None, 
                 message: Optional[Message] = None,
                 parent=None):
        super().__init__(parent)
        self.entity_type = entity_type
        self.message = message
        self.mode = 'get_profile' if entity_type else 'log_message'

    def run(self):
        try:
            agent = DatasetAgent()
            if self.mode == 'get_profile':
                profile = agent.get_or_create_profile(self.entity_type)
                self.profile_ready.emit(profile)
            else:
                agent.log_message(self.message)
                self.logging_complete.emit(True)
        except Exception as e:
            self.error_occurred.emit(f"Dataset error: {str(e)}")
        finally:
            self.finished_signal.emit()
```

# backend/agents/mistral_agent.py

```py
import os
from PySide6 import QtCore as qtc
from mistralai import Mistral

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

# backend/models/message.py

```py
from datetime import datetime
from typing import Optional

class Message:
    def __init__(self, conversation_id: str, sender_id: str, content: str, 
                 created_at: Optional[datetime] = None, id: Optional[int] = None):
        self.id = id
        self.conversation_id = conversation_id
        self.sender_id = sender_id
        self.content = content
        self.created_at = created_at if created_at else datetime.now()
```

# backend/models/profile.py

```py
from datetime import datetime
from typing import Optional

class Profile:
    def __init__(self, entity_type: str, id: Optional[str] = None, 
                 created_at: Optional[datetime] = None, 
                 last_used_at: Optional[datetime] = None):
        self.id = id
        self.entity_type = entity_type
        self.created_at = created_at if created_at else datetime.now()
        self.last_used_at = last_used_at
```

# build.sh

```sh
#!/usr/bin/env bash

# Cross-platform build script for MyChatBot Docker image

set -euo pipefail

# Get the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Build using compose (preferred)
if command -v docker-compose &> /dev/null || command -v docker compose &> /dev/null; then
  cd "$PROJECT_ROOT"
  docker-compose build --no-cache
elif command -v docker &> /dev/null; then
  cd "$PROJECT_ROOT"
  docker build -t mychatbot:latest \
    --label "project=mychatbot" \
    --label "maintainer=$(whoami)@$(hostname)" \
    .
else
  echo "Error: Neither docker-compose nor docker command found"
  exit 1
fi

echo "Build completed successfully"
```

# cleanup.sh

```sh
#!/usr/bin/env bash

# Cross-platform cleanup script for MyChatBot Docker resources

set -euo pipefail

# Get the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Function to safely remove resources
safe_remove() {
  local filter="$1"
  local type="$2"
  
  echo "Removing $type with filter: $filter"
  if ! docker "$type" ls --filter "$filter" --format "{{.ID}}" | xargs -r docker "$type" rm -f 2>/dev/null; then
    echo "No $type to remove"
  fi
}

# Stop and remove containers
if command -v docker-compose &> /dev/null || command -v docker compose &> /dev/null; then
  cd "$PROJECT_ROOT"
  docker-compose -f "docker-compose.yml" down || true
fi

# Remove project-specific resources
safe_remove "label=project=mychatbot" "container"
safe_remove "label=project=mychatbot" "image"
safe_remove "name=mychatbot" "network"
safe_remove "name=mychatbot" "volume"

# Cleanup builder cache
docker builder prune -f --filter "label=project=mychatbot" 2>/dev/null || true

# Cleanup networks (not associated with containers)
docker network prune -f 2>/dev/null || true

echo "Cleanup complete"
```

# docker-compose.yml

```yml
version: '3.8'

services:
  mychatbot:
    build:
      context: .
      args:
        PROJECT_NAME: mychatbot
    labels:
      - "project=mychatbot"
    volumes:
      - ./.env:/app/.env
      - ./backend:/app/backend
      - /tmp/.X11-unix:/tmp/.X11-unix
    environment:
      - DISPLAY=${DISPLAY}
      - QT_X11_NO_MITSHM=1
    tty: true
    stdin_open: true
```

# dockerfile

```
# Stage 1: Builder
FROM python:3.10-slim AS builder

# Set project metadata
ARG PROJECT_NAME=mychatbot
LABEL project=$PROJECT_NAME \
      maintainer="your@email.com" \
      version="1.0.0"

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.10-slim

# Copy project metadata
ARG PROJECT_NAME=mychatbot
LABEL project=$PROJECT_NAME \
      maintainer="your@email.com" \
      version="1.0.0"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxkbcommon0 \
    libegl1 \
    libxcb1 \
    libx11-xcb1 \
    libx11-6 \
    libfontconfig1 \
    libdbus-1-3 \
    libxcb-cursor0 \
    libglx0 \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create directory for the database
RUN mkdir -p /app/backend

# Environment variables
ENV PYTHONPATH=/app
ENV QT_DEBUG_PLUGINS=1
ENV QT_X11_NO_MITSHM=1

# Run the application
CMD ["python", "main.py"]
```

# frontend/components/chat_message.py

```py
from PySide6 import QtWidgets as qtw
from PySide6 import QtCore as qtc
from PySide6 import QtGui as qtg
from datetime import datetime
import markdown

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

# frontend/components/loading_widget.py

```py
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
```

# frontend/controllers/main_controller.py

```py
from PySide6 import QtCore as qtc
from pathlib import Path
import base64
import uuid
from backend.agents.mistral_agent import MistralWorker
from backend.agents.dataset_agent import DatasetAgentWorker
from backend.models.message import Message
from backend.models.profile import Profile

class MainController(qtc.QObject):
    display_user_message = qtc.Signal(str)
    display_ai_message = qtc.Signal(str)

    show_loading = qtc.Signal()
    hide_loading = qtc.Signal()

    error_occurred = qtc.Signal(str)

    def __init__(self):
        super().__init__()
        self.conversation_id = str(uuid.uuid4())
        self.user_profile = None
        self.ai_profile = None
        self.worker_threads = []
        
        self.init_profiles()

    def init_profiles(self):
        user_worker = DatasetAgentWorker(entity_type='user')
        user_worker.profile_ready.connect(self.set_user_profile)
        user_worker.error_occurred.connect(
            lambda e: print(f"Error getting user profile: {e}"))
        user_worker.finished_signal.connect(self.cleanup_thread)
        self.worker_threads.append(user_worker)
        user_worker.start()
        
        ai_worker = DatasetAgentWorker(entity_type='ai')
        ai_worker.profile_ready.connect(self.set_ai_profile)
        ai_worker.error_occurred.connect(
            lambda e: print(f"Error getting AI profile: {e}"))
        ai_worker.finished_signal.connect(self.cleanup_thread)
        self.worker_threads.append(ai_worker)
        ai_worker.start()

    def set_user_profile(self, profile: Profile):
        self.user_profile = profile
        print(f"User profile set: {profile.id}")

    def set_ai_profile(self, profile: Profile):
        self.ai_profile = profile
        print(f"AI profile set: {profile.id}")

    def send_message(self, message_text: str):
        if not message_text or not self.user_profile:
            return
        
        self.display_user_message.emit(message_text)
            
        # Create message object
        message = Message(
            conversation_id=self.conversation_id,
            sender_id=self.user_profile.id,
            content=message_text
        )
        
        # Log the message
        self.log_message(message)
        
        self.show_loading.emit()

        # Send to Mistral
        self.send_to_mistral(message_text)

    def send_to_mistral(self, prompt: str):
        worker = MistralWorker(prompt)
        worker.response_received.connect(self.handle_response)
        worker.error_occurred.connect(self.handle_error)
        worker.finished_signal.connect(self.cleanup_thread)
        self.worker_threads.append(worker)
        worker.start()

    def handle_response(self, response: str):
        self.hide_loading.emit()

        self.display_ai_message.emit(response)

        if not self.ai_profile:
            return
            
        # Create message object for AI response
        message = Message(
            conversation_id=self.conversation_id,
            sender_id=self.ai_profile.id,
            content=response
        )
        
        # Log the message
        self.log_message(message)

    def handle_error(self, error: str):
        self.hide_loading.emit()
        self.error_occurred.emit(error)

    def log_message(self, message: Message):
        worker = DatasetAgentWorker(message=message)
        worker.logging_complete.connect(
            lambda success: print("Message logged" if success else "Failed to log message"))
        worker.error_occurred.connect(
            lambda error: print(f"Error logging message: {error}"))
        worker.finished_signal.connect(self.cleanup_thread)
        self.worker_threads.append(worker)
        worker.start()

    def attach_file(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                filename = Path(file_path).name
                return f"Here is the content of file '{filename}':\n\n{content}\n\nPlease analyze this file."
        except Exception as e:
            return f"Error reading file: {str(e)}"

    def attach_image(self, image_path: str):
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            
            filename = Path(image_path).name
            return f"Here is an image named '{filename}' (base64 encoded):\n\n{encoded_string}\n\nPlease analyze this image."
        except Exception as e:
            return f"Error processing image: {str(e)}"

    def cleanup_thread(self):
        self.worker_threads = [t for t in self.worker_threads if t.isRunning()]
```

# frontend/views/main_window.py

```py
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
```

# LICENSE.txt

```txt

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

```

# main.py

```py
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
```

# README.md

```md
# MyChatBot

Welcome to MyChatBot. A PySide6-based application that uses Mistal AI API for users to send messages, attach files and images, and view responses from the Mistrl AI. This project was not hand written by me. This project serves as my first attempt at AI prompting. I elected to do something small with interacting with the AI and creating a raw, unsanitized dataset from those interactions. Each dataset is saved to a relational database on your system as I support user privacy. You may do with these datasets as you please. These prompts are done using DeekSeek and ChatGPT. It's for me to obtain an idea of how I'm going to build my model.

Total Prompts: 
23- deepseek

each "prompt" is considered an input message from me with/without files/images attached

## Features

- **User Interface**: A clean and intuitive chat interface built with PySide6.
- **Message Logging**: Messages are logged into an SQLite database.
- **File and Image Attachments**: Users can attach and send files and images.
- **Markdown Support**: Messages can be formatted using Markdown.
- **Concurrency**: Uses QThread for background tasks to keep the UI responsive.

## Project Structure

\`\`\`
.
├── .env
├── .gitignore
├── chat_dataset.db
├── chat_widget.py
├── dataset_agent.py
├── main.py
├── mistral_agent.py
├── requirements.txt
└── README.md
\`\`\`

## Prerequisites

- Python 3.x

## Installation

1. Clone the repository:

    \`\`\`sh
    git clone https://github.com/mek0124/MyChatBot
    cd MyChatBot
    \`\`\`

2. Create a virtual environment and activate it:

    \`\`\`sh
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    \`\`\`

3. Install the required dependencies:

    \`\`\`sh
    pip install -r requirements.txt
    \`\`\`

4. Set up the environment variables by creating a `.env` file in the project root:

    \`\`\`ini
    MISTRAL_API_KEY=your_mistral_api_key_here # do not encase in double quotes!
    \`\`\`

## Running the Application

To run the application, execute the following command:

\`\`\`sh
python main.py

# python3 main.py if on linux/mac
\`\`\`

## Codebase Overview

### `.gitignore`

Specifies files and directories to be ignored by Git.

### `chat_dataset.db`

> .gitignored by default

A binary file containing the SQLite database used to store chat profiles and messages.

### `chat_widget.py`

Contains the custom PySide6 widgets used in the chat interface:

- **LoadingWidget**: Displays a loading animation.
- **ChatMessageWidget**: Displays chat messages with Markdown support and options to copy or save messages.

### `dataset_agent.py`

Handles interactions with the SQLite database:

- **DatasetAgent**: Manages database operations for profiles and messages.
- **DatasetAgentWorker**: A QThread for performing database operations in the background.

### `main.py`

The main entry point of the application:

- **MainWindow**: The main window class that sets up the UI and handles user interactions.
- Initializes profiles for the user and AI.
- Manages sending messages and handling responses.

### `mistral_agent.py`

Handles interactions with the Mistral AI API:

- **MistralWorker**: A QThread for sending messages to the Mistral AI API and receiving responses.

### `requirements.txt`

Lists the Python dependencies required to run the application.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Thanks to the Mistral AI team for providing the API.
- Thanks to the PySide6 community for their excellent UI framework.

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

# run.sh

```sh
#!/usr/bin/env bash

# Cross-platform run script for MyChatBot

set -euo pipefail

# Get the directory containing this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# Detect OS and handle X11 forwarding
case "$(uname -s)" in
  Linux*)
    xhost +local:root >/dev/null 2>&1 || true
    X11_ARGS=(-e "DISPLAY=$DISPLAY" -v "/tmp/.X11-unix:/tmp/.X11-unix")
    ;;
  Darwin*)
    xhost +localhost >/dev/null 2>&1 || true
    X11_ARGS=(-e "DISPLAY=host.docker.internal:0" -v "/tmp/.X11-unix:/tmp/.X11-unix")
    ;;
  *)
    X11_ARGS=()
    ;;
esac

# Run using compose (preferred)
if command -v docker-compose &> /dev/null || command -v docker compose &> /dev/null; then
  cd "$PROJECT_ROOT"
  docker-compose -f "docker-compose.yml" up
elif command -v docker &> /dev/null; then
  docker run -it --rm \
    "${X11_ARGS[@]}" \
    -v "$PROJECT_ROOT/.env:/app/.env" \
    -v "$PROJECT_ROOT/backend:/app/backend" \
    --name mychatbot \
    mychatbot:latest
else
  echo "Error: Neither docker-compose nor docker command found"
  exit 1
fi

# Cleanup X11 access
case "$(uname -s)" in
  Linux*) xhost -local:root >/dev/null 2>&1 || true ;;
  Darwin*) xhost -localhost >/dev/null 2>&1 || true ;;
esac
```

