from typing import Optional
from .base import CodaModel

class Challenge(CodaModel):
    TABLE_ID = "grid-frCt4QLI3B"
    COLS = {
        "user_id": "colUserId",
        "prompt_id": "colPromptId",
        "status": "colStatus",
        "score": "colScore",
        "feedback": "colFeedback",
        "attempts": "colAttempts",
        "last_attempt": "colLastAttempt",
    }

    def __init__(
        self,
        user_id: str,
        prompt_id: str,
        status: str,
        score: float,
        feedback: str,
        attempts: int,
        last_attempt: str,
        _row_id: Optional[str] = None
    ):
        self.user_id = user_id
        self.prompt_id = prompt_id
        self.status = status
        self.score = score
        self.feedback = feedback
        self.attempts = attempts
        self.last_attempt = last_attempt
        self._row_id = _row_id 