import pytest
from datetime import datetime
from models.user import User
from codaio import Coda

class TestUserModel:
    def test_create_user_from_row(self):
        """Test creating a User instance from a Coda row"""
        row = {
            'id': 'row_id_123',
            'values': {
                'username': 'testuser',
                'user_id': 'user_123',
                'user_email': 'test@example.com',
                'user_first_name': 'Test',
                'user_last_name': 'User',
                'user_password': 'hashed_password',
                'user_session_ids': ['session_1', 'session_2'],
                'user_created_at': '2024-03-20T10:00:00Z',
                'user_updated_at': '2024-03-20T10:00:00Z'
            }
        }
        
        user = User.from_row(row)
        
        assert user.username == 'testuser'
        assert user.user_id == 'user_123'
        assert user.user_email == 'test@example.com'
        assert user.user_first_name == 'Test'
        assert user.user_last_name == 'User'
        assert user.user_password == 'hashed_password'
        assert user.user_session_ids == ['session_1', 'session_2']
        assert isinstance(user.user_created_at, datetime)
        assert isinstance(user.user_updated_at, datetime)
        assert user._row_id == 'row_id_123'

    def test_convert_to_coda_cells(self):
        """Test converting a User instance to Coda cells"""
        user = User(
            username='testuser',
            user_id='user_123',
            user_email='test@example.com',
            user_first_name='Test',
            user_last_name='User',
            user_password='hashed_password',
            user_session_ids=['session_1', 'session_2']
        )
        
        cells = user.to_coda_cells()
        
        assert len(cells) == 9  # All fields including timestamps
        assert any(cell['column'] == 'username' and cell['value'] == 'testuser' for cell in cells)
        assert any(cell['column'] == 'user_id' and cell['value'] == 'user_123' for cell in cells)
        assert any(cell['column'] == 'user_email' and cell['value'] == 'test@example.com' for cell in cells)

    def test_validation_required_fields(self):
        """Test validation of required fields"""
        with pytest.raises(ValueError):
            User(
                username='testuser',
                # Missing user_id
                user_email='test@example.com',
                user_first_name='Test',
                user_last_name='User',
                user_password='hashed_password'
            )

    def test_get_full_name(self):
        """Test getting user's full name"""
        user = User(
            username='testuser',
            user_id='user_123',
            user_email='test@example.com',
            user_first_name='Test',
            user_last_name='User',
            user_password='hashed_password'
        )
        
        assert user.get_full_name() == 'Test User'

    def test_add_session_id(self):
        """Test adding a session ID to user's sessions"""
        user = User(
            username='testuser',
            user_id='user_123',
            user_email='test@example.com',
            user_first_name='Test',
            user_last_name='User',
            user_password='hashed_password',
            user_session_ids=['session_1']
        )
        
        user.add_session_id('session_2')
        assert 'session_2' in user.user_session_ids
        assert len(user.user_session_ids) == 2

    def test_get_by_username(self, monkeypatch):
        """Test retrieving a user by username"""
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
        
        user = User.get_by_username(None, None, 'testuser')
        assert user is not None
        assert user.username == 'testuser'
        assert user.user_id == 'user_123'

    def test_get_by_id(self, monkeypatch):
        """Test retrieving a user by user_id"""
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
        
        user = User.get_by_id(None, None, 'user_123')
        assert user is not None
        assert user.user_id == 'user_123'
        assert user.username == 'testuser'

    def test_get_by_email(self, monkeypatch):
        """Test retrieving a user by email"""
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
        
        user = User.get_by_email(None, None, 'test@example.com')
        assert user is not None
        assert user.user_email == 'test@example.com'
        assert user.username == 'testuser' 