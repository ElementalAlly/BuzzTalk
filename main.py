import os
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
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

def get_channels(server: str = "woodruff") -> List[str]:
    name_ind = 0
    description_ind = 1
    connection = pymysql.connect(host="localhost",
                                 user=LOCAL_USER,
                                 password=LOCAL_PASSWORD,
                                 database="BuzzTalk")
    with connection:
        with connection.cursor() as cursor:
            query = f"SELECT * from {server}_channels;"
            cursor.execute(query)
            raw_data = list(cursor.fetchall())

    result: List[str] = []
    for entry in raw_data:
        result.append(entry[name_ind])
    
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

@app.get("/", response_class=RedirectResponse)
def read_root():
    return "/channel/general"

@app.get("/channel/{channel_name}")
async def view_posts(channel_name: str):
    if channel_name == None:
        channel_name = "general"
    db = get_posts(0, channel_name)
    return page_generator.generate_posts_page(db, channel_name, get_channels())

@app.get("/make_channel", response_class=HTMLResponse)
async def get_channels_page(server: str = "woodruff"):
    return page_generator.generate_channels_page(get_channels())

@app.post("/api/posts")
def create_post(channel: str = None, title: str = Form(...), content: str = Form(...)):
    make_post(0, "you", title, content, channel)
    return RedirectResponse(url=f"/channel/{channel}", status_code=303)

@app.post("/api/reply")
def create_reply(reply_id: int, channel: str, reply: str = Form(...)):
    make_post(reply_id, "me", None, reply, channel)
    return RedirectResponse(url=f"/channel/{channel}", status_code=303)

@app.get("/logo")
def get_logo():
    return FileResponse("logo/BuzzTalkLogo.jpeg")