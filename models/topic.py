from typing import Optional
from .base import CodaModel

class Topic(CodaModel):
    TABLE_ID = "tblTopics"
    COLS = {
        "name": "colName",
        "description": "colDescription",
        "category": "colCategory",
        "level": "colLevel",
        "status": "colStatus",
        "skill_id": "colSkillId",
    }

    def __init__(
        self,
        name: str,
        description: str,
        category: str,
        level: str,
        status: str,
        skill_id: str,
        _row_id: Optional[str] = None
    ):
        self.name = name
        self.description = description
        self.category = category
        self.level = level
        self.status = status
        self.skill_id = skill_id
        self._row_id = _row_id 