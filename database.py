from typing import Optional, List, Dict
from datetime import datetime
import uuid
from models import User, UserInDB, UserCreate, Post, PostCreate, Comment, CommentCreate, Vote
from auth import get_password_hash

users_db: Dict[str, UserInDB] = {}
posts_db: Dict[str, Post] = {}
comments_db: Dict[str, Comment] = {}
votes_db: Dict[str, Vote] = {}

def get_user_by_username(username: str) -> Optional[User]:
    user_in_db = users_db.get(username)
    if user_in_db:
        return User(**user_in_db.dict())
    return None

def get_user_by_id(user_id: str) -> Optional[User]:
    for user in users_db.values():
        if user.id == user_id:
            return User(**user.dict())
    return None

def authenticate_user(username: str, password: str) -> Optional[User]:
    user = users_db.get(username)
    if not user:
        return None
    from auth import verify_password
    if not verify_password(password, user.hashed_password):
        return None
    return User(**user.dict())

def create_user(user: UserCreate) -> User:
    if user.username in users_db:
        raise ValueError("Username already exists")

    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user.password)

    user_in_db = UserInDB(
        id=user_id,
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        created_at=datetime.utcnow(),
        karma=0,
        is_active=True
    )

    users_db[user.username] = user_in_db
    return User(**user_in_db.dict())

def create_post(post: PostCreate, author: User) -> Post:
    post_id = str(uuid.uuid4())

    new_post = Post(
        id=post_id,
        title=post.title,
        content=post.content,
        url=post.url,
        author_id=author.id,
        author_username=author.username,
        created_at=datetime.utcnow(),
        upvotes=0,
        downvotes=0,
        score=0,
        comment_count=0
    )

    posts_db[post_id] = new_post
    return new_post

def get_post_by_id(post_id: str) -> Optional[Post]:
    return posts_db.get(post_id)

def get_posts(skip: int = 0, limit: int = 100) -> List[Post]:
    posts = list(posts_db.values())
    posts.sort(key=lambda x: x.created_at, reverse=True)
    return posts[skip:skip + limit]

def update_post(post_id: str, title: Optional[str] = None, content: Optional[str] = None) -> Optional[Post]:
    post = posts_db.get(post_id)
    if not post:
        return None

    if title is not None:
        post.title = title
    if content is not None:
        post.content = content

    return post

def delete_post(post_id: str) -> bool:
    if post_id in posts_db:
        del posts_db[post_id]
        for comment_id in list(comments_db.keys()):
            if comments_db[comment_id].post_id == post_id:
                del comments_db[comment_id]
        return True
    return False

def create_comment(comment: CommentCreate, author: User) -> Comment:
    comment_id = str(uuid.uuid4())

    new_comment = Comment(
        id=comment_id,
        content=comment.content,
        post_id=comment.post_id,
        parent_comment_id=comment.parent_comment_id,
        author_id=author.id,
        author_username=author.username,
        created_at=datetime.utcnow(),
        upvotes=0,
        downvotes=0,
        score=0,
        replies=[]
    )

    comments_db[comment_id] = new_comment

    if comment.post_id in posts_db:
        posts_db[comment.post_id].comment_count += 1

    return new_comment

def get_comments_by_post(post_id: str) -> List[Comment]:
    post_comments = [c for c in comments_db.values() if c.post_id == post_id]
    post_comments.sort(key=lambda x: x.created_at)
    return post_comments

def vote_on_post(post_id: str, user: User, is_upvote: bool) -> Optional[Post]:
    post = posts_db.get(post_id)
    if not post:
        return None

    vote_id = f"{user.id}_{post_id}_post"
    existing_vote = votes_db.get(vote_id)

    if existing_vote:
        if existing_vote.is_upvote != is_upvote:
            existing_vote.is_upvote = is_upvote
            if is_upvote:
                post.upvotes += 1
                post.downvotes -= 1
            else:
                post.upvotes -= 1
                post.downvotes += 1
    else:
        vote = Vote(
            id=vote_id,
            user_id=user.id,
            post_id=post_id,
            is_upvote=is_upvote,
            created_at=datetime.utcnow()
        )
        votes_db[vote_id] = vote

        if is_upvote:
            post.upvotes += 1
        else:
            post.downvotes += 1

    post.score = post.upvotes - post.downvotes
    return post

def vote_on_comment(comment_id: str, user: User, is_upvote: bool) -> Optional[Comment]:
    comment = comments_db.get(comment_id)
    if not comment:
        return None

    vote_id = f"{user.id}_{comment_id}_comment"
    existing_vote = votes_db.get(vote_id)

    if existing_vote:
        if existing_vote.is_upvote != is_upvote:
            existing_vote.is_upvote = is_upvote
            if is_upvote:
                comment.upvotes += 1
                comment.downvotes -= 1
            else:
                comment.upvotes -= 1
                comment.downvotes += 1
    else:
        vote = Vote(
            id=vote_id,
            user_id=user.id,
            comment_id=comment_id,
            is_upvote=is_upvote,
            created_at=datetime.utcnow()
        )
        votes_db[vote_id] = vote

        if is_upvote:
            comment.upvotes += 1
        else:
            comment.downvotes += 1

    comment.score = comment.upvotes - comment.downvotes
    return comment
