from typing import Optional
from .base import CodaModel

class Skill(CodaModel):
    TABLE_ID = "grid-VZpWaIP27c"  # Update if your table ID is differentgrid-VZpWaIP27c
    COLS = {
        "skill_name": "skill_name",
        "skill_agent_prompt": "skill_agent_prompt",
        "skill_teach_description": "skill_teach_description",
        "Conversations": "Conversations",
        "conversation_id": "conversation_id",
    }

    def __init__(
        self,
        skill_name: str,
        skill_agent_prompt: str,
        skill_teach_description: str,
        Conversations: str,
        conversation_id: str,
        _row_id: Optional[str] = None
    ):
        self.skill_name = skill_name
        self.skill_agent_prompt = skill_agent_prompt
        self.skill_teach_description = skill_teach_description
        self.Conversations = Conversations
        self.conversation_id = conversation_id
        self._row_id = _row_id 