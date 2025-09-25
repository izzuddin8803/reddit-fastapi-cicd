# Reddit-like FastAPI Application

A Reddit-like social media API built with FastAPI, featuring user authentication, posts, comments, and voting system. Perfect for learning CI/CD and PR workflows.

## Features

- **User Management**: Registration, authentication with JWT tokens
- **Posts**: Create, read, update, delete posts with voting system
- **Comments**: Comment on posts with voting support
- **Voting System**: Upvote/downvote posts and comments
- **Authorization**: Users can only edit/delete their own content
- **In-memory Storage**: Data resets when server restarts
- **Comprehensive Testing**: Unit and integration tests included

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Authentication
- `POST /register` - Register a new user
- `POST /token` - Login and get access token
- `GET /users/me` - Get current user info

### Posts
- `POST /posts/` - Create a new post (auth required)
- `GET /posts/` - Get all posts
- `GET /posts/{id}` - Get specific post
- `PUT /posts/{id}` - Update post (auth required, own posts only)
- `DELETE /posts/{id}` - Delete post (auth required, own posts only)
- `POST /posts/{id}/vote` - Vote on a post (auth required)

### Comments
- `POST /posts/{post_id}/comments/` - Add comment to post (auth required)
- `GET /posts/{post_id}/comments/` - Get comments for a post
- `POST /comments/{id}/vote` - Vote on a comment (auth required)

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest

# Run unit tests only
pytest test_unit.py -v

# Run integration tests only
pytest test_integration.py -v
```

## Test Coverage

### Unit Tests (3 meaningful tests):
1. **Password Hashing Test**: Validates password hashing and verification
2. **User Creation Test**: Tests user creation and duplicate prevention
3. **Voting Logic Test**: Tests post voting mechanics and vote changes

### Integration Tests (3 comprehensive flows):
1. **User Registration & Auth Flow**: Complete user journey from registration to authenticated access
2. **Post Lifecycle Test**: Full CRUD operations on posts with authorization checks
3. **Post Interaction Flow**: Creates posts, votes, comments with proper integration

## Example Usage

### Register a user:
```bash
curl -X POST "http://localhost:8000/register" \
     -H "Content-Type: application/json" \
     -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'
```

### Login:
```bash
curl -X POST "http://localhost:8000/token" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "username=testuser&password=password123"
```

### Create a post:
```bash
curl -X POST "http://localhost:8000/posts/" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -d '{"title": "My First Post", "content": "Hello Reddit-like API!"}'
```