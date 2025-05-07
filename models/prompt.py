from typing import List, Optional
from codaio import Coda, Document, Row, Cell

class Prompt:
    TABLE_ID = "grid-vBrJKADk0W"
    
    def __init__(
        self,
        prompt_description: str,
        topics: str,
        prompt_user: str,
        audio: str,
        text: str,
        context: str,
        topic_code: str,
        prompt_code: str,
        level: str,
        audio_url: str,
        audio_url_txt: str,
        language_name: str,
        language_code: str,
        flag: str,
        _row_id: Optional[str] = None
    ):
        self.prompt_description = prompt_description
        self.topics = topics
        self.prompt_user = prompt_user
        self.audio = audio
        self.text = text
        self.context = context
        self.topic_code = topic_code
        self.prompt_code = prompt_code
        self.level = level
        self.audio_url = audio_url
        self.audio_url_txt = audio_url_txt
        self.language_name = language_name
        self.language_code = language_code
        self.flag = flag
        self._row_id = _row_id

    @classmethod
    def from_row(cls, row: Row) -> 'Prompt':
        """Create a Prompt from a codaio Row object"""
        data = row.to_dict()
        return cls(
            prompt_description=data.get("prompt_description", ""),
            topics=data.get("topics", ""),
            prompt_user=data.get("prompt_user", ""),
            audio=data.get("audio", ""),
            text=data.get("text", ""),
            context=data.get("context", ""),
            topic_code=data.get("topic_code", ""),
            prompt_code=data.get("prompt_code", ""),
            level=data.get("level", ""),
            audio_url=data.get("audio_url", ""),
            audio_url_txt=data.get("audio_url_txt", ""),
            language_name=data.get("language_name", ""),
            language_code=data.get("language_code", ""),
            flag=data.get("flag", ""),
            _row_id=row.id
        )

    def to_cells(self) -> List[Cell]:
        """Convert to codaio Cell objects for create/update"""
        return [
            Cell(column="prompt_description", value_storage=self.prompt_description),
            Cell(column="topics", value_storage=self.topics),
            Cell(column="prompt_user", value_storage=self.prompt_user),
            Cell(column="audio", value_storage=self.audio),
            Cell(column="text", value_storage=self.text),
            Cell(column="context", value_storage=self.context),
            Cell(column="topic_code", value_storage=self.topic_code),
            Cell(column="prompt_code", value_storage=self.prompt_code),
            Cell(column="level", value_storage=self.level),
            Cell(column="audio_url", value_storage=self.audio_url),
            Cell(column="audio_url_txt", value_storage=self.audio_url_txt),
            Cell(column="language_name", value_storage=self.language_name),
            Cell(column="language_code", value_storage=self.language_code),
            Cell(column="flag", value_storage=self.flag)
        ]

    @classmethod
    def get_all(cls, coda: Coda, doc_id: str) -> List['Prompt']:
        """Get all prompts from Coda"""
        doc = Document(doc_id, coda=coda)
        table = doc.get_table(cls.TABLE_ID)
        return [cls.from_row(row) for row in table.rows()]

    @classmethod
    def get_by_user(cls, coda: Coda, doc_id: str, username: str) -> List['Prompt']:
        """Get all prompts for a specific user"""
        return [p for p in cls.get_all(coda, doc_id) if p.prompt_user == username]

    @classmethod
    def filter(cls, coda: Coda, doc_id: str, **filters) -> List['Prompt']:
        """Filter prompts by multiple criteria
        
        Args:
            coda: Coda API client
            doc_id: Coda document ID
            **filters: Keyword arguments for filtering (e.g., prompt_user="john", level="A1")
        
        Returns:
            List of prompts matching all filter criteria
        """
        prompts = cls.get_all(coda, doc_id)
        
        for field, value in filters.items():
            if hasattr(cls, field):
                prompts = [p for p in prompts if getattr(p, field) == value]
        
        return prompts

    def save(self, coda: Coda, doc_id: str) -> 'Prompt':
        """Save the prompt to Coda (create or update)"""
        doc = Document(doc_id, coda=coda)
        table = doc.get_table(self.TABLE_ID)
        
        if self._row_id:
            # Update existing row
            row = table[self._row_id]
            for cell in self.to_cells():
                row[cell.column] = cell.value_storage
            return self.from_row(row)
        else:
            # Create new row
            row = table.upsert_row(self.to_cells())
            return self.from_row(row) 