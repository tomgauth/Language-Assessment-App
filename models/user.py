from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class User:
    """Pure data structure representing a user in the system."""
    username: str
    user_id: str
    user_email: str
    user_first_name: str
    user_last_name: str
    user_password: str
    user_data_joined: Optional[str] = None
    user_level: Optional[str] = None
    user_challenges: Optional[str] = None
    prompt_table_id: Optional[str] = None
    user_document_id: Optional[str] = None

    @property
    def full_name(self) -> str:
        """Returns the user's full name."""
        return f"{self.user_first_name} {self.user_last_name}"

    @property
    def has_user_document(self) -> bool:
        """Returns whether the user has a personal document."""
        return bool(self.user_document_id)

    @property
    def has_prompt_table(self) -> bool:
        """Returns whether the user has a prompt table."""
        return bool(self.prompt_table_id)

