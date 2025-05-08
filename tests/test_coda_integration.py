import pytest
from models.prompt import Prompt
from codaio import Coda

class TestCodaIntegration:
    def test_get_all_prompts(self, coda_client, doc_id):
        """Test retrieving all prompts from Coda"""
        prompts = Prompt.get_all(coda_client, doc_id)
        assert len(prompts) > 0
        assert all(isinstance(p, Prompt) for p in prompts)
        
        # Check structure of first prompt
        first_prompt = prompts[0]
        assert hasattr(first_prompt, 'prompt_description')
        assert hasattr(first_prompt, 'prompt_code')
        assert hasattr(first_prompt, 'conversations')
        assert hasattr(first_prompt, 'topics')

    def test_get_prompts_by_user(self, coda_client, doc_id):
        """Test retrieving prompts for a specific user"""
        # Get a known user from the database
        all_prompts = Prompt.get_all(coda_client, doc_id)
        if not all_prompts:
            pytest.skip("No prompts in database")
        
        test_user = all_prompts[0].prompt_user
        user_prompts = Prompt.get_by_user(coda_client, doc_id, test_user)
        
        assert len(user_prompts) > 0
        assert all(p.prompt_user == test_user for p in user_prompts)

    def test_get_prompts_by_conversation(self, coda_client, doc_id):
        """Test retrieving prompts for a specific conversation"""
        # Get a known conversation from the database
        all_prompts = Prompt.get_all(coda_client, doc_id)
        if not all_prompts:
            pytest.skip("No prompts in database")
        
        test_conversation = all_prompts[0].conversations
        conversation_prompts = Prompt.get_by_conversation(coda_client, doc_id, test_conversation)
        
        assert len(conversation_prompts) > 0
        assert all(p.conversations == test_conversation for p in conversation_prompts)

    def test_get_prompts_by_topic(self, coda_client, doc_id):
        """Test retrieving prompts for a specific topic"""
        # Get a known topic from the database
        all_prompts = Prompt.get_all(coda_client, doc_id)
        if not all_prompts:
            pytest.skip("No prompts in database")
        
        test_topic = all_prompts[0].topics
        topic_prompts = Prompt.get_by_topic(coda_client, doc_id, test_topic)
        
        assert len(topic_prompts) > 0
        assert all(p.topics == test_topic for p in topic_prompts)

    def test_get_random_prompt(self, coda_client, doc_id):
        """Test getting a random prompt for a conversation and topic"""
        # Get known conversation and topic from database
        all_prompts = Prompt.get_all(coda_client, doc_id)
        if not all_prompts:
            pytest.skip("No prompts in database")
        
        test_conversation = all_prompts[0].conversations
        test_topic = all_prompts[0].topics
        
        # Get random prompt
        prompt = Prompt.get_random_prompt(coda_client, doc_id, test_conversation, test_topic)
        
        assert prompt is not None
        assert prompt.conversations == test_conversation
        assert prompt.topics == test_topic

    def test_error_handling_invalid_doc_id(self, coda_client):
        """Test error handling with invalid document ID"""
        with pytest.raises(Exception):
            Prompt.get_all(coda_client, "invalid_doc_id")

    def test_error_handling_invalid_user(self, coda_client, doc_id):
        """Test error handling with invalid user"""
        prompts = Prompt.get_by_user(coda_client, doc_id, "nonexistent_user")
        assert len(prompts) == 0

    def test_error_handling_invalid_conversation(self, coda_client, doc_id):
        """Test error handling with invalid conversation"""
        prompts = Prompt.get_by_conversation(coda_client, doc_id, "nonexistent_conversation")
        assert len(prompts) == 0

    def test_error_handling_invalid_topic(self, coda_client, doc_id):
        """Test error handling with invalid topic"""
        prompts = Prompt.get_by_topic(coda_client, doc_id, "nonexistent_topic")
        assert len(prompts) == 0

    def test_prompt_data_consistency(self, coda_client, doc_id):
        """Test consistency of prompt data from Coda"""
        prompts = Prompt.get_all(coda_client, doc_id)
        if not prompts:
            pytest.skip("No prompts in database")
        
        for prompt in prompts:
            # Check all required fields are present
            assert prompt.prompt_description is not None
            assert prompt.prompt_code is not None
            assert prompt.conversations is not None
            assert prompt.topics is not None
            assert prompt.prompt_user is not None
            
            # Check field types
            assert isinstance(prompt.prompt_description, str)
            assert isinstance(prompt.prompt_code, str)
            assert isinstance(prompt.conversations, str)
            assert isinstance(prompt.topics, str)
            assert isinstance(prompt.prompt_user, str) 