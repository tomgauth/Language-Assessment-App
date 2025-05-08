from typing import Optional
from .base import CodaModel

class User(CodaModel):
    TABLE_ID = "grid-qqR8f6GhaA"  # Update if your table ID is different
    COLS = {
        "username": "username",
        "user_first_name": "user_first_name",
        "user_last_name": "user_last_name",
    }

    def __init__(
        self,
        username: str,
        user_first_name: str,
        user_last_name: str,
        _row_id: Optional[str] = None
    ):
        self.username = username
        self.user_first_name = user_first_name
        self.user_last_name = user_last_name
        self._row_id = _row_id