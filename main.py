import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, ConfigDict
from typing import List
import pymysql.cursors

import page_generator

class Post(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: int
    parent_id: int
    username: str
    title: str
    body: str
    replies: []

app = FastAPI()

from dotenv import load_dotenv
load_dotenv()

LOCAL_USER = os.getenv("user")
LOCAL_PASSWORD = os.getenv("password")

def get_posts(parent: int, channel: str) -> List[Post]:
    post_id_ind = 0
    parent_id_ind = 1
    channel_ind = 2
    username_ind = 3
    post_time_ind = 4
    title_ind = 5
    body_ind = 6
    connection = pymysql.connect(host="localhost",
                                 user=LOCAL_USER,
                                 password=LOCAL_PASSWORD,
                                 database="BuzzTalk")
    with connection:
        with connection.cursor() as cursor:
            query = f"""SELECT * FROM woodruff
            WHERE parent_id = {parent} and channel = '{channel}';"""
            cursor.execute(query)
            raw_data = list(cursor.fetchall())

    result: List[Post] = []
    for entry in raw_data:
        result.append(Post(id=entry[post_id_ind],
                           parent_id=entry[parent_id_ind],
                           username=entry[username_ind],
                           title=entry[title_ind],
                           body=entry[body_ind],
                           replies=get_posts(entry[post_id_ind], channel)))

    return result

def make_post(parent_id: int, username: str, title: str, body: str, channel: str):
    connection = pymysql.connect(host="localhost",
                                 user=LOCAL_USER,
                                 password=LOCAL_PASSWORD,
                                 database="BuzzTalk")
    with connection:
        with connection.cursor() as cursor:
            query = f"""INSERT INTO woodruff
            (parent_id, channel, post_time, username, title, body)
            VALUES
            ({parent_id}, '{channel}', CURRENT_TIMESTAMP, '{username}', '{title}', '{body}');"""
            print(query)
            cursor.execute(query)
        connection.commit()


def traverse_post(post: Post, layer: int, channel: str):
    if layer == 0:
        result = f"""
            <div class="comment" style="border: 1px solid #ccc; padding: 10px; margin-bottom: 10px;">
                <h3>{post.title} (ID: {post.id}, layer: {layer})</h3>
                <p>{post.body}</p>
                <button class="reply-button">Reply</button>
                <div class="reply-box" style="display: none;">
                    <form action="/api/reply?reply_id={post.id}&channel={channel}", method="post">
                        <textarea name="reply" rows="4" placeholder="Post Reply" required></textarea><br>
                        <button type="submit">Post</button>
                    </form>
                    <button class="cancel">Cancel</button>
                </div>
        """
    else:
        result = f"""
            <div class="comment" style="border: 1px solid #ccc; padding: 10px; margin-bottom: 10px;">
                <p>(ID: {post.id}, layer: {layer})</p>
                <p>{post.body}</p>
                <button class="reply-button">Reply</button>
                <div class="reply-box" style="display: none;">
                    <form action="/api/reply?reply_id={post.id}&channel={channel}", method="post">
                        <textarea name="reply" rows="4" placeholder="Post Reply" required></textarea><br>
                        <button type="submit">Post</button>
                    </form>
                    <button class="cancel">Cancel</button>
                </div>
        """
    for i in range(len(post.replies)):
        result = result + traverse_post(post.replies[i], layer + 1, channel)
    
    result  = result + "</div>"
    return result


def generate_html_response(channel: str):
    if channel == None:
        channel = "None"
    db = get_posts(0, channel)
    return page_generator.generate_posts_page(db, channel)
    """posts_html = ""
    db = get_posts(0, channel)
    for post in reversed(db):  # Show new posts at the top
        posts_html += traverse_post(post, 0, channel)

    html_content = f""
    <html>
        <head>
            <title>My FastAPI Forum</title>
            <style>
                body {{ font-family: sans-serif; margin: 2em; }}
                input, textarea {{ width: 100%; padding: 8px; margin-bottom: 10px; box-sizing: border-box; }}
                button {{ padding: 10px 15px; background-color: #007BFF; color: white; border: none; cursor: pointer; }}
                button:hover {{ background-color: #0056b3; }}
    /* ------------------------------ */
    /* TOP NAVIGATION BAR            */
    /* ------------------------------ */
    .navbar {
      width: 100%;
      background-color: #ffffff;
      height: 56px;
      display: flex;
      align-items: center;
      padding: 0 16px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      position: fixed;
      top: 0;
      left: 0;
      z-index: 1000;
    }

    .navbar-logo {
      font-size: 20px;
      font-weight: bold;
      margin-right: auto;
    }

    .menu-button {
      font-size: 24px;
      cursor: pointer;
      border: none;
      background: none;
    }

    /* ------------------------------ */
    /* SIDEBAR                       */
    /* ------------------------------ */
    .sidebar {
      position: fixed;
      top: 56px; /* below nav bar */
      left: 0;
      width: 0;
      height: 100%;
      background-color: #ffffff;
      overflow-x: hidden;
      transition: width 0.3s ease;
      border-right: 1px solid #ccc;
      padding-top: 20px;
      z-index: 999;
    }

    .sidebar.open {
      width: 250px;
    }

    .sidebar a {
      display: block;
      padding: 12px 20px;
      text-decoration: none;
      color: #333;
      font-size: 16px;
    }

    .sidebar a:hover {
      background-color: #f0f0f0;
    }
        channel = None
            </style>
        </head>
        <body>
            <h1>Welcome to My Forum</h1>
            <h2>Create a New Post in {channel}</h2>
            <form action="/api/posts?channel={channel}" method="post">
                <input type="text" name="title" placeholder="Post Title" required><br>
                <textarea name="content" rows="4" placeholder="Post Content" required></textarea><br>
                <button type="submit">Post</button>
            </form>
            <hr>
            <h2>Post List: {channel}</h2>
            {posts_html}
            <script>
                // Find all reply buttons
                const replyButtons = document.querySelectorAll('.reply-button');

                replyButtons.forEach(button => {{
                    const comment = button.closest('.comment');
                    const replyBox = comment.querySelector('.reply-box');
                    const cancelButton = comment.querySelector('.cancel');

                    // Toggle the reply box when clicking "Reply"
                    button.addEventListener('click', () => {{
                        const isVisible = replyBox.style.display === 'block';
                        replyBox.style.display = isVisible ? 'none' : 'block';
                    }});

                    // Hide it when clicking "Cancel"
                    cancelButton.addEventListener('click', () => {{
                        replyBox.style.display = 'none';
                    }});
                }});
            </script>
        </body>
    </html>
    ""
    return HTMLResponse(content=html_content, status_code=200)
    """

@app.get("/", response_class=RedirectResponse)
def read_root():
    return "/posts"

@app.get("/posts", response_class=HTMLResponse)
async def view_posts():
    return generate_html_response(None)

@app.get("/channel/{channel_name}")
async def view_posts(channel_name: str):
    return generate_html_response(channel_name)

@app.get("/api/posts", response_model=List[Post])
def api_posts():
    return get_posts(0, None)

@app.post("/api/posts")
def create_post(channel: str = None, title: str = Form(...), content: str = Form(...)):
    make_post(0, "you", title, content, channel)
    return RedirectResponse(url=f"/channel/{channel}", status_code=303)

@app.post("/api/reply")
def create_reply(reply_id: int, channel: str, reply: str = Form(...)):
    make_post(reply_id, "me", None, reply, channel)
    return RedirectResponse(url=f"/channel/{channel}", status_code=303)