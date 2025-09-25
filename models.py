from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
import uuid


class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    created_at: datetime
    karma: int = 0
    is_active: bool = True

    class Config:
        from_attributes = True

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class PostBase(BaseModel):
    title: str
    content: Optional[str] = None
    url: Optional[str] = None

class PostCreate(PostBase):
    pass

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class Post(PostBase):
    id: str
    author_id: str
    author_username: str
    created_at: datetime
    upvotes: int = 0
    downvotes: int = 0
    score: int = 0
    comment_count: int = 0

    class Config:
        from_attributes = True

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    post_id: str
    parent_comment_id: Optional[str] = None

class Comment(CommentBase):
    id: str
    post_id: str
    author_id: str
    author_username: str
    parent_comment_id: Optional[str] = None
    created_at: datetime
    upvotes: int = 0
    downvotes: int = 0
    score: int = 0
    replies: List['Comment'] = []

    class Config:
        from_attributes = True

class VoteBase(BaseModel):
    is_upvote: bool

class Vote(VoteBase):
    id: str
    user_id: str
    post_id: Optional[str] = None
    comment_id: Optional[str] = None
    created_at: datetime
