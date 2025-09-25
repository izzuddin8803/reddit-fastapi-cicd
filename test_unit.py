import pytest
from datetime import datetime
from models import UserCreate, PostCreate, CommentCreate, User
from auth import get_password_hash, verify_password, create_access_token
import database

@pytest.fixture(autouse=True)
def clear_database():
    database.users_db.clear()
    database.posts_db.clear()
    database.comments_db.clear()
    database.votes_db.clear()
    yield

class TestPasswordHashing:
    def test_password_hashing_and_verification(self):
        """Test that password hashing and verification work correctly"""
        plain_password = "test_password_123"
        hashed_password = get_password_hash(plain_password)

        assert hashed_password != plain_password
        assert verify_password(plain_password, hashed_password) is True
        assert verify_password("wrong_password", hashed_password) is False

    def test_different_passwords_produce_different_hashes(self):
        """Test that the same password produces different hashes each time (salt)"""
        password = "same_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True

class TestUserCreation:
    def test_create_user_success(self):
        """Test successful user creation"""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123"
        )

        created_user = database.create_user(user_data)

        assert created_user.username == "testuser"
        assert created_user.email == "test@example.com"
        assert created_user.id is not None
        assert created_user.karma == 0
        assert created_user.is_active is True
        assert created_user.created_at is not None

    def test_create_duplicate_username_fails(self):
        """Test that creating a user with duplicate username fails"""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123"
        )

        database.create_user(user_data)

        with pytest.raises(ValueError, match="Username already exists"):
            database.create_user(user_data)

class TestVotingLogic:
    def setup_method(self):
        """Set up test data for voting tests"""
        self.user = database.create_user(UserCreate(
            username="voter",
            email="voter@example.com",
            password="password123"
        ))

        self.post = database.create_post(PostCreate(
            title="Test Post",
            content="This is a test post"
        ), self.user)

    def test_upvote_post(self):
        """Test upvoting a post increases score correctly"""
        initial_score = self.post.score
        initial_upvotes = self.post.upvotes

        updated_post = database.vote_on_post(self.post.id, self.user, is_upvote=True)

        assert updated_post.upvotes == initial_upvotes + 1
        assert updated_post.score == initial_score + 1

    def test_downvote_post(self):
        """Test downvoting a post decreases score correctly"""
        initial_score = self.post.score
        initial_downvotes = self.post.downvotes

        updated_post = database.vote_on_post(self.post.id, self.user, is_upvote=False)

        assert updated_post.downvotes == initial_downvotes + 1
        assert updated_post.score == initial_score - 1

    def test_change_vote_from_upvote_to_downvote(self):
        """Test changing vote from upvote to downvote"""
        database.vote_on_post(self.post.id, self.user, is_upvote=True)
        initial_upvotes = self.post.upvotes
        initial_downvotes = self.post.downvotes

        updated_post = database.vote_on_post(self.post.id, self.user, is_upvote=False)

        assert updated_post.upvotes == initial_upvotes - 1
        assert updated_post.downvotes == initial_downvotes + 1
        assert updated_post.score == -1