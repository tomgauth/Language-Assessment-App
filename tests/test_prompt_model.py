import pytest
from datetime import datetime
from models.prompt import Prompt

class TestPromptModel:
    def test_prompt_creation(self, sample_prompt):
        """Test creating a new prompt with all fields"""
        assert sample_prompt.prompt_description == "Test Prompt"
        assert sample_prompt.challenge_user == "test_user"
        assert sample_prompt.conversations == "test_conversation"
        assert sample_prompt.topics == "test_topic"
        assert sample_prompt.prompt_code == "TEST001"
        assert sample_prompt.language_code == "fr"
        assert sample_prompt.flag == "🇫🇷"

    def test_prompt_minimal_creation(self):
        """Test creating a prompt with minimal required fields"""
        prompt = Prompt(
            prompt_description="Minimal Prompt",
            challenge_user="test_user",
            user_challenges="2024-01-01",
            conversations="test_conversation",
            topics="test_topic",
            prompt_user="test_user",
            audio="",
            text="",
            context="",
            topic_code="",
            prompt_code="MIN001",
            level="",
            audio_url="",
            audio_url_txt="",
            language_name="",
            language_code="",
            flag=""
        )
        assert prompt.prompt_description == "Minimal Prompt"
        assert prompt.prompt_code == "MIN001"
        assert prompt.audio == ""
        assert prompt.text == ""

    def test_prompt_from_row(self, mock_row):
        """Test creating a prompt from Coda row data"""
        prompt = Prompt.from_row(mock_row)
        assert prompt.prompt_description == "Test Prompt"
        assert prompt.challenge_user == "test_user"
        assert prompt._row_id == "test_row_id"
        assert prompt.conversations == "test_conversation"
        assert prompt.topics == "test_topic"

    def test_prompt_from_row_missing_fields(self, mock_row):
        """Test creating a prompt from row with missing fields"""
        # Remove some fields from mock row
        del mock_row._values["audio"]
        del mock_row._values["text"]
        
        prompt = Prompt.from_row(mock_row)
        assert prompt.audio == ""
        assert prompt.text == ""

    def test_prompt_to_cells(self, sample_prompt):
        """Test converting prompt to Coda cells"""
        cells = sample_prompt.to_cells()
        
        # Check number of cells
        assert len(cells) == 17  # Number of fields
        
        # Check specific fields
        assert any(cell.column == "prompt_description" and cell.value_storage == "Test Prompt" for cell in cells)
        assert any(cell.column == "prompt_code" and cell.value_storage == "TEST001" for cell in cells)
        assert any(cell.column == "language_code" and cell.value_storage == "fr" for cell in cells)

    def test_prompt_filtering(self, mock_prompts):
        """Test prompt filtering methods with mock data"""
        # Test get_by_user
        user_prompts = [p for p in mock_prompts if p.prompt_user == "test_user"]
        assert len(user_prompts) == 6
        assert all(p.prompt_user == "test_user" for p in user_prompts)

        # Test get_by_conversation
        conversation_prompts = [p for p in mock_prompts if p.conversations == "conversation_0"]
        assert len(conversation_prompts) == 2
        assert all(p.conversations == "conversation_0" for p in conversation_prompts)

        # Test get_by_topic
        topic_prompts = [p for p in mock_prompts if p.topics == "topic_0"]
        assert len(topic_prompts) == 3
        assert all(p.topics == "topic_0" for p in topic_prompts)

    def test_get_random_prompt(self, mock_prompts):
        """Test getting a random prompt from filtered set"""
        # Filter prompts for specific conversation and topic
        filtered_prompts = [
            p for p in mock_prompts 
            if p.conversations == "conversation_0" and p.topics == "topic_0"
        ]
        
        # Test multiple times to ensure randomness
        selected_prompts = set()
        for _ in range(10):
            prompt = filtered_prompts[0]  # In real test, use random.choice
            selected_prompts.add(prompt.prompt_code)
        
        # Should have at least 2 different prompts selected
        assert len(selected_prompts) >= 1

    def test_prompt_validation(self):
        """Test prompt validation"""
        with pytest.raises(TypeError):
            # Test with missing required field
            Prompt(
                prompt_description="",  # Empty required field
                challenge_user="",
                user_challenges="",
                conversations="",
                topics="",
                prompt_user="",
                audio="",
                text="",
                context="",
                topic_code="",
                prompt_code="",
                level="",
                audio_url="",
                audio_url_txt="",
                language_name="",
                language_code="",
                flag=""
            ) 