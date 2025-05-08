from typing import List, Optional
from models.user import User
from models.challenge import Challenge
from models.conversation import Conversation
from models.skill import Skill
from models.topic import Topic
from models.prompt import Prompt
from codaio import Coda, Document

class CodaDatabaseService:
    def __init__(self, api_token: str, doc_id: str):
        self.coda = Coda(api_token)
        self.doc = Document(doc_id, coda=self.coda)

    # ───────── Users ─────────
    def get_users(self) -> List[User]:
        table = self.doc.get_table(User.TABLE_ID)
        return [User.from_row(row) for row in table.rows()]

    def get_user(self, username: str) -> Optional[User]:
        rows = self.get_users()
        for u in rows:
            if u.username == username:
                return u
        return None

    def create_user(self, user: User) -> User:
        table = self.doc.get_table(User.TABLE_ID)
        row = table.upsert_row([Cell(column=col, value_storage=val) for col, val in user.to_coda_payload().items()])
        return User.from_row(row)

    def update_user(self, user: User) -> User:
        assert user._row_id, "need row_id to update"
        table = self.doc.get_table(User.TABLE_ID)
        row = table[user._row_id]
        for col, val in user.to_coda_payload().items():
            row[col] = val
        return User.from_row(row)

    # ───────── Challenges ─────────
    def get_challenges_for_user(self, user: User) -> List[Challenge]:
        table = self.doc.get_table(Challenge.TABLE_ID)
        return [Challenge.from_row(row) for row in table.rows() if row['user_id'] == user._row_id]

    def create_challenge(self, challenge: Challenge) -> Challenge:
        table = self.doc.get_table(Challenge.TABLE_ID)
        row = table.upsert_row([Cell(column=col, value_storage=val) for col, val in challenge.to_coda_payload().items()])
        return Challenge.from_row(row)

    # ───────── Conversations ─────────
    def get_conversations_for_user(self, user: User) -> List[Conversation]:
        table = self.doc.get_table(Conversation.TABLE_ID)
        return [Conversation.from_row(row) for row in table.rows() if row['user_id'] == user._row_id]

    def create_conversation(self, conv: Conversation) -> Conversation:
        table = self.doc.get_table(Conversation.TABLE_ID)
        row = table.upsert_row([Cell(column=col, value_storage=val) for col, val in conv.to_coda_payload().items()])
        return Conversation.from_row(row)

    # ───────── Skills, Topics, Prompts ─────────
    def list_skills(self) -> List[Skill]:
        table = self.doc.get_table(Skill.TABLE_ID)
        return [Skill.from_row(row) for row in table.rows()]

    def list_topics(self) -> List[Topic]:
        table = self.doc.get_table(Topic.TABLE_ID)
        return [Topic.from_row(row) for row in table.rows()]

    def list_prompts(self) -> List[Prompt]:
        table = self.doc.get_table(Prompt.TABLE_ID)
        return [Prompt.from_row(row) for row in table.rows()]

    def create_prompt(self, p: Prompt) -> Prompt:
        table = self.doc.get_table(Prompt.TABLE_ID)
        row = table.upsert_row([Cell(column=col, value_storage=val) for col, val in p.to_coda_payload().items()])
        return Prompt.from_row(row) 