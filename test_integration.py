import pytest
from fastapi.testclient import TestClient
from main import app
import database

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_database():
    database.users_db.clear()
    database.posts_db.clear()
    database.comments_db.clear()
    database.votes_db.clear()
    yield

@pytest.fixture
def authenticated_user():
    """Create a user and return authentication token"""
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }

    response = client.post("/register", json=user_data)
    assert response.status_code == 200

    login_data = {
        "username": "testuser",
        "password": "password123"
    }

    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}

class TestUserRegistrationAndAuth:
    def test_complete_user_registration_and_login_flow(self):
        """Test the complete flow from registration to authenticated access"""
        user_data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword123"
        }

        register_response = client.post("/register", json=user_data)
        assert register_response.status_code == 200
        user = register_response.json()
        assert user["username"] == "newuser"
        assert user["email"] == "newuser@example.com"
        assert "id" in user

        login_data = {
            "username": "newuser",
            "password": "securepassword123"
        }
        login_response = client.post("/token", data=login_data)
        assert login_response.status_code == 200
        token_data = login_response.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"

        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        me_response = client.get("/users/me", headers=headers)
        assert me_response.status_code == 200
        user_me = me_response.json()
        assert user_me["username"] == "newuser"

    def test_duplicate_username_registration_fails(self):
        """Test that registering with a duplicate username fails properly"""
        user_data = {
            "username": "duplicate",
            "email": "first@example.com",
            "password": "password123"
        }

        first_response = client.post("/register", json=user_data)
        assert first_response.status_code == 200

        user_data["email"] = "second@example.com"
        second_response = client.post("/register", json=user_data)
        assert second_response.status_code == 400
        assert "Username already exists" in second_response.json()["detail"]

class TestPostManagement:
    def test_complete_post_lifecycle(self, authenticated_user):
        """Test creating, reading, updating, and deleting posts"""
        headers = authenticated_user

        post_data = {
            "title": "My First Post",
            "content": "This is the content of my first post",
            "url": "https://example.com"
        }

        create_response = client.post("/posts/", json=post_data, headers=headers)
        assert create_response.status_code == 200
        created_post = create_response.json()
        assert created_post["title"] == "My First Post"
        assert created_post["content"] == "This is the content of my first post"
        assert "id" in created_post
        post_id = created_post["id"]

        get_response = client.get(f"/posts/{post_id}")
        assert get_response.status_code == 200
        fetched_post = get_response.json()
        assert fetched_post["id"] == post_id
        assert fetched_post["title"] == "My First Post"

        update_data = {
            "title": "Updated Post Title",
            "content": "Updated content"
        }
        update_response = client.put(f"/posts/{post_id}", json=update_data, headers=headers)
        assert update_response.status_code == 200
        updated_post = update_response.json()
        assert updated_post["title"] == "Updated Post Title"
        assert updated_post["content"] == "Updated content"

        delete_response = client.delete(f"/posts/{post_id}", headers=headers)
        assert delete_response.status_code == 200

        get_deleted_response = client.get(f"/posts/{post_id}")
        assert get_deleted_response.status_code == 404

    def test_unauthorized_post_operations(self, authenticated_user):
        """Test that unauthorized users cannot modify posts they don't own"""
        headers = authenticated_user

        post_data = {
            "title": "Owner's Post",
            "content": "This post belongs to the first user"
        }

        create_response = client.post("/posts/", json=post_data, headers=headers)
        assert create_response.status_code == 200
        post_id = create_response.json()["id"]

        other_user_data = {
            "username": "otheruser",
            "email": "other@example.com",
            "password": "password123"
        }
        client.post("/register", json=other_user_data)

        login_data = {"username": "otheruser", "password": "password123"}
        login_response = client.post("/token", data=login_data)
        other_token = login_response.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}

        update_data = {"title": "Trying to steal this post"}
        update_response = client.put(f"/posts/{post_id}", json=update_data, headers=other_headers)
        assert update_response.status_code == 403

        delete_response = client.delete(f"/posts/{post_id}", headers=other_headers)
        assert delete_response.status_code == 403

class TestPostVotingAndComments:
    def test_complete_post_interaction_flow(self, authenticated_user):
        """Test creating a post, voting on it, and adding comments"""
        headers = authenticated_user

        post_data = {
            "title": "Popular Post",
            "content": "This post will get votes and comments"
        }

        create_response = client.post("/posts/", json=post_data, headers=headers)
        assert create_response.status_code == 200
        post = create_response.json()
        post_id = post["id"]
        assert post["upvotes"] == 0
        assert post["score"] == 0

        upvote_data = {"is_upvote": True}
        vote_response = client.post(f"/posts/{post_id}/vote", json=upvote_data, headers=headers)
        assert vote_response.status_code == 200
        voted_post = vote_response.json()
        assert voted_post["upvotes"] == 1
        assert voted_post["score"] == 1

        comment_data = {
            "content": "This is a great post!",
            "post_id": post_id
        }

        comment_response = client.post(f"/posts/{post_id}/comments/", json=comment_data, headers=headers)
        assert comment_response.status_code == 200
        comment = comment_response.json()
        assert comment["content"] == "This is a great post!"
        assert comment["post_id"] == post_id
        comment_id = comment["id"]

        get_comments_response = client.get(f"/posts/{post_id}/comments/")
        assert get_comments_response.status_code == 200
        comments = get_comments_response.json()
        assert len(comments) == 1
        assert comments[0]["id"] == comment_id

        comment_upvote_data = {"is_upvote": True}
        comment_vote_response = client.post(f"/comments/{comment_id}/vote", json=comment_upvote_data, headers=headers)
        assert comment_vote_response.status_code == 200
        voted_comment = comment_vote_response.json()
        assert voted_comment["upvotes"] == 1
        assert voted_comment["score"] == 1

        get_updated_post_response = client.get(f"/posts/{post_id}")
        updated_post = get_updated_post_response.json()
        assert updated_post["comment_count"] == 1
