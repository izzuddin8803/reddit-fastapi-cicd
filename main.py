from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from datetime import timedelta

from models import User, UserCreate, Post, PostCreate, PostUpdate, Comment, CommentCreate, Token, VoteBase
from auth import authenticate_user, create_access_token, get_current_active_user, ACCESS_TOKEN_EXPIRE_MINUTES
import database

app = FastAPI(title="Reddit-like API", version="1.0.0", description="A Reddit-like social media API")

@app.get("/")
async def root():
    return {"message": "Welcome to Reddit-like API"}

@app.post("/register", response_model=User)
async def register_user(user: UserCreate):
    try:
        return database.create_user(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.post("/posts/", response_model=Post)
async def create_post(
    post: PostCreate,
    current_user: User = Depends(get_current_active_user)
):
    return database.create_post(post, current_user)

@app.get("/posts/", response_model=List[Post])
async def get_posts(skip: int = 0, limit: int = 100):
    return database.get_posts(skip=skip, limit=limit)

@app.get("/posts/{post_id}", response_model=Post)
async def get_post(post_id: str):
    post = database.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@app.put("/posts/{post_id}", response_model=Post)
async def update_post(
    post_id: str,
    post_update: PostUpdate,
    current_user: User = Depends(get_current_active_user)
):
    post = database.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to edit this post")

    updated_post = database.update_post(
        post_id,
        title=post_update.title,
        content=post_update.content
    )
    return updated_post

@app.delete("/posts/{post_id}")
async def delete_post(
    post_id: str,
    current_user: User = Depends(get_current_active_user)
):
    post = database.get_post_by_id(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")

    database.delete_post(post_id)
    return {"message": "Post deleted successfully"}

@app.post("/posts/{post_id}/vote", response_model=Post)
async def vote_on_post(
    post_id: str,
    vote: VoteBase,
    current_user: User = Depends(get_current_active_user)
):
    updated_post = database.vote_on_post(post_id, current_user, vote.is_upvote)
    if not updated_post:
        raise HTTPException(status_code=404, detail="Post not found")
    return updated_post

@app.post("/posts/{post_id}/comments/", response_model=Comment)
async def create_comment(
    post_id: str,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_active_user)
):
    if comment_data.post_id != post_id:
        comment_data.post_id = post_id

    if not database.get_post_by_id(post_id):
        raise HTTPException(status_code=404, detail="Post not found")

    return database.create_comment(comment_data, current_user)

@app.get("/posts/{post_id}/comments/", response_model=List[Comment])
async def get_comments(post_id: str):
    return database.get_comments_by_post(post_id)

@app.post("/comments/{comment_id}/vote", response_model=Comment)
async def vote_on_comment(
    comment_id: str,
    vote: VoteBase,
    current_user: User = Depends(get_current_active_user)
):
    updated_comment = database.vote_on_comment(comment_id, current_user, vote.is_upvote)
    if not updated_comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return updated_comment

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
