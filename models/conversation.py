from typing import Optional
from .base import CodaModel

class Conversation(CodaModel):
    TABLE_ID = "tblConversations"
    COLS = {
        "user_id": "colUserId",
        "prompt_id": "colPromptId",
        "transcript": "colTranscript",
        "audio_url": "colAudioURL",
        "duration": "colDuration",
        "created_at": "colCreatedAt",
        "status": "colStatus",
    }

    def __init__(
        self,
        user_id: str,
        prompt_id: str,
        transcript: str,
        audio_url: str,
        duration: float,
        created_at: str,
        status: str,
        _row_id: Optional[str] = None
    ):
        self.user_id = user_id
        self.prompt_id = prompt_id
        self.transcript = transcript
        self.audio_url = audio_url
        self.duration = duration
        self.created_at = created_at
        self.status = status
        self._row_id = _row_id 