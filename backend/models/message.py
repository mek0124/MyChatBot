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