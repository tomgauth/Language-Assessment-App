import pytest
from codaio import Coda, Row
from datetime import datetime
from models.prompt import Prompt
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

@pytest.fixture
def coda_client():
    """Fixture to provide a Coda client for testing"""
    api_key = os.getenv("CODA_API_KEY")
    if not api_key:
        pytest.skip("CODA_API_KEY not set in environment")
    return Coda(api_key)

@pytest.fixture
def doc_id():
    """Fixture to provide the Coda document ID for testing"""
    doc_id = os.getenv("CODA_DOC_ID")
    if not doc_id:
        pytest.skip("CODA_DOC_ID not set in environment")
    return doc_id

@pytest.fixture
def mock_row():
    """Fixture to provide a mock Coda row for testing"""
    class MockRow:
        def __init__(self):
            self.id = "test_row_id"
            self._values = {
                "prompt_description": "Test Prompt",
                "challenge_user": "test_user",
                "user_challenges": "2024-01-01",
                "conversations": "test_conversation",
                "topics": "test_topic",
                "prompt_user": "test_user",
                "audio": "test_audio.mp3",
                "text": "Test text",
                "context": "Test context",
                "topic_code": "TEST",
                "prompt_code": "TEST001",
                "level": "A1",
                "audio_url": "https://test.com/audio.mp3",
                "audio_url_txt": "https://test.com/audio.txt",
                "language_name": "French",
                "language_code": "fr",
                "flag": "🇫🇷"
            }
        
        def to_dict(self):
            return self._values
    
    return MockRow()

@pytest.fixture
def sample_prompt():
    """Fixture to provide a sample prompt for testing"""
    return Prompt(
        prompt_description="Test Prompt",
        challenge_user="test_user",
        user_challenges="2024-01-01",
        conversations="test_conversation",
        topics="test_topic",
        prompt_user="test_user",
        audio="test_audio.mp3",
        text="Test text",
        context="Test context",
        topic_code="TEST",
        prompt_code="TEST001",
        level="A1",
        audio_url="https://test.com/audio.mp3",
        audio_url_txt="https://test.com/audio.txt",
        language_name="French",
        language_code="fr",
        flag="🇫🇷"
    )

@pytest.fixture
def mock_prompts():
    """Fixture to provide a list of mock prompts for testing"""
    return [
        Prompt(
            prompt_description=f"Test Prompt {i}",
            challenge_user="test_user",
            user_challenges="2024-01-01",
            conversations=f"conversation_{i % 3}",  # 3 different conversations
            topics=f"topic_{i % 2}",  # 2 different topics
            prompt_user="test_user",
            audio=f"test_audio_{i}.mp3",
            text=f"Test text {i}",
            context=f"Test context {i}",
            topic_code=f"TEST{i:03d}",
            prompt_code=f"PROMPT{i:03d}",
            level="A1",
            audio_url=f"https://test.com/audio_{i}.mp3",
            audio_url_txt=f"https://test.com/audio_{i}.txt",
            language_name="French",
            language_code="fr",
            flag="🇫🇷"
        ) for i in range(6)  # Create 6 test prompts
    ] 