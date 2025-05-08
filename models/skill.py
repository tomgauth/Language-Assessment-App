from typing import Optional
from .base import CodaModel

class Skill(CodaModel):
    TABLE_ID = "tblSkills"
    COLS = {
        "name": "colName",
        "description": "colDescription",
        "category": "colCategory",
        "level": "colLevel",
        "status": "colStatus",
    }

    def __init__(
        self,
        name: str,
        description: str,
        category: str,
        level: str,
        status: str,
        _row_id: Optional[str] = None
    ):
        self.name = name
        self.description = description
        self.category = category
        self.level = level
        self.status = status
        self._row_id = _row_id 