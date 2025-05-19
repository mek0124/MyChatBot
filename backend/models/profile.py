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