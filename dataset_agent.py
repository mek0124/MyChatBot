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