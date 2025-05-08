import pytest
from datetime import datetime
from models.coda_service import CodaService
from models.user import User
from models.prompt import Prompt

class TestCodaService:
    @pytest.fixture
    def coda_service(self):
        """Create a CodaService instance for testing"""
        return CodaService('test_api_key', 'test_doc_id')

    def test_get_all_users(self, coda_service, monkeypatch):
        """Test retrieving all users"""
        def mock_get_all(coda, doc_id):
            return [
                User(
                    username='testuser',
                    user_id='user_123',
                    user_email='test@example.com',
                    user_first_name='Test',
                    user_last_name='User',
                    user_password='hashed_password'
                )
            ]
        
        monkeypatch.setattr(User, 'get_all', mock_get_all)
        
        users = coda_service.get_all_users()
        assert len(users) == 1
        assert users[0].username == 'testuser'
        assert users[0].user_id == 'user_123'

    def test_get_user_by_username(self, coda_service, monkeypatch):
        """Test retrieving a user by username"""
        def mock_get_by_username(coda, doc_id, username):
            if username == 'testuser':
                return User(
                    username='testuser',
                    user_id='user_123',
                    user_email='test@example.com',
                    user_first_name='Test',
                    user_last_name='User',
                    user_password='hashed_password'
                )
            return None
        
        monkeypatch.setattr(User, 'get_by_username', mock_get_by_username)
        
        user = coda_service.get_user_by_username('testuser')
        assert user is not None
        assert user.username == 'testuser'
        assert user.user_id == 'user_123'

        user = coda_service.get_user_by_username('nonexistent')
        assert user is None

    def test_create_user(self, coda_service, monkeypatch):
        """Test creating a new user"""
        def mock_save(coda, doc_id):
            return User(
                username='newuser',
                user_id='user_456',
                user_email='new@example.com',
                user_first_name='New',
                user_last_name='User',
                user_password='hashed_password'
            )
        
        monkeypatch.setattr(User, 'save', mock_save)
        
        user = coda_service.create_user(
            username='newuser',
            user_id='user_456',
            user_email='new@example.com',
            user_first_name='New',
            user_last_name='User',
            user_password='hashed_password'
        )
        
        assert user.username == 'newuser'
        assert user.user_id == 'user_456'
        assert user.user_email == 'new@example.com'

    def test_update_user(self, coda_service, monkeypatch):
        """Test updating an existing user"""
        def mock_save(coda, doc_id):
            return User(
                username='updateduser',
                user_id='user_123',
                user_email='updated@example.com',
                user_first_name='Updated',
                user_last_name='User',
                user_password='hashed_password',
                _row_id='row_123'
            )
        
        monkeypatch.setattr(User, 'save', mock_save)
        
        user = User(
            username='updateduser',
            user_id='user_123',
            user_email='updated@example.com',
            user_first_name='Updated',
            user_last_name='User',
            user_password='hashed_password',
            _row_id='row_123'
        )
        
        updated_user = coda_service.update_user(user)
        assert updated_user.username == 'updateduser'
        assert updated_user.user_email == 'updated@example.com'

        with pytest.raises(ValueError):
            user_without_row = User(
                username='testuser',
                user_id='user_123',
                user_email='test@example.com',
                user_first_name='Test',
                user_last_name='User',
                user_password='hashed_password'
            )
            coda_service.update_user(user_without_row)

    def test_get_all_prompts(self, coda_service, monkeypatch):
        """Test retrieving all prompts"""
        def mock_get_all(coda, doc_id):
            return [
                Prompt(
                    prompt_id='prompt_123',
                    prompt_text='Test prompt',
                    prompt_audio='audio_url',
                    prompt_context='Test context',
                    prompt_user='testuser',
                    prompt_conversation='conversation_1',
                    prompt_topic='topic_1'
                )
            ]
        
        monkeypatch.setattr(Prompt, 'get_all', mock_get_all)
        
        prompts = coda_service.get_all_prompts()
        assert len(prompts) == 1
        assert prompts[0].prompt_id == 'prompt_123'
        assert prompts[0].prompt_text == 'Test prompt'

    def test_get_prompts_by_user(self, coda_service, monkeypatch):
        """Test retrieving prompts by user"""
        def mock_get_by_user(coda, doc_id, username):
            return [
                Prompt(
                    prompt_id='prompt_123',
                    prompt_text='Test prompt',
                    prompt_audio='audio_url',
                    prompt_context='Test context',
                    prompt_user='testuser',
                    prompt_conversation='conversation_1',
                    prompt_topic='topic_1'
                )
            ]
        
        monkeypatch.setattr(Prompt, 'get_by_user', mock_get_by_user)
        
        prompts = coda_service.get_prompts_by_user('testuser')
        assert len(prompts) == 1
        assert prompts[0].prompt_user == 'testuser'
        assert prompts[0].prompt_id == 'prompt_123'

    def test_get_random_prompt(self, coda_service, monkeypatch):
        """Test retrieving a random prompt"""
        def mock_get_random_prompt(coda, doc_id, conversation, topic):
            return Prompt(
                prompt_id='prompt_123',
                prompt_text='Test prompt',
                prompt_audio='audio_url',
                prompt_context='Test context',
                prompt_user='testuser',
                prompt_conversation='conversation_1',
                prompt_topic='topic_1'
            )
        
        monkeypatch.setattr(Prompt, 'get_random_prompt', mock_get_random_prompt)
        
        prompt = coda_service.get_random_prompt('conversation_1', 'topic_1')
        assert prompt is not None
        assert prompt.prompt_conversation == 'conversation_1'
        assert prompt.prompt_topic == 'topic_1'
        assert prompt.prompt_id == 'prompt_123' 