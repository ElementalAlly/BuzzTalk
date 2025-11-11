from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, ConfigDict
from typing import List
import pymysql.cursors

class Post(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: int
    parent_id: int
    username: str
    title: str
    content: str
    replies: []

app = FastAPI()

db: List[Post] = [
    Post(id=1, title="What is FastAPI?", content="api go fast", replies=
         [Post(id=2, title="What am I?", content="api go slow", replies=[])]),
    Post(id=2, title="Introduction to pydantic", content="Pydantic is data verification :D", replies=[])
]

def traverse_post(post: Post, layer: int):
    result = f"""
        <div style="border: 1px solid #ccc; padding: 10px; margin-bottom: 10px;">
            <h3>{post.title} (ID: {post.id}, layer: {layer})</h3>
            <p>{post.content}</p>
    """
    for i in range(len(post.replies)):
        result = result + traverse_post(post.replies[i], layer + 1)
    
    result  = result + "</div>"
    return result


def generate_html_response():
    posts_html = ""
    for post in reversed(db):  # Show new posts at the top
        posts_html += traverse_post(post, 0)

    html_content = f"""
    <html>
        <head>
            <title>My FastAPI Forum</title>
            <style>
                body {{ font-family: sans-serif; margin: 2em; }}
                input, textarea {{ width: 100%; padding: 8px; margin-bottom: 10px; box-sizing: border-box; }}
                button {{ padding: 10px 15px; background-color: #007BFF; color: white; border: none; cursor: pointer; }}
                button:hover {{ background-color: #0056b3; }}
            </style>
        </head>
        <body>
            <h1>Welcome to My Forum</h1>
            <h2>Create a New Post</h2>
            <form action="/api/posts" method="post">
                <input type="text" name="title" placeholder="Post Title" required><br>
                <textarea name="content" rows="4" placeholder="Post Content" required></textarea><br>
                <button type="submit">Post</button>
            </form>
            <hr>
            <h2>Post List</h2>
            {posts_html}
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/", response_class=RedirectResponse)
def read_root():
    return "/posts"

@app.get("/posts", response_class=HTMLResponse)
async def view_posts():
    return generate_html_response()

@app.get("/api/posts", response_model=List[Post])
def get_posts():
    return db

@app.post("/api/posts")
def create_post(title: str = Form(...), content: str = Form(...)):
    new_id = len(db) + 1
    new_post = Post(
        id = new_id,
        title = title,
        content=content
    )
    db.append(new_post)
    return RedirectResponse(url="/posts", status_code=303)