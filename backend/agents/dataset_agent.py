import sqlite3
import uuid
from typing import Optional
from PySide6 import QtCore as qtc
from ..models.message import Message
from ..models.profile import Profile

class DatasetAgent:
    def __init__(self, db_path: str = "chat_dataset.db"):
        self.db_path = db_path
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