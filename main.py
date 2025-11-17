import os
from fastapi import FastAPI, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from pydantic import BaseModel, ConfigDict
from typing import List, Annotated
import pymysql.cursors
import datetime

import page_generator

class Post(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: int
    parent_id: int
    channel: str
    username: str
    timestamp: str
    title: str
    body: str
    replies: []

app = FastAPI()

from dotenv import load_dotenv
load_dotenv()

LOCAL_USER = os.getenv("user")
LOCAL_PASSWORD = os.getenv("password")

def get_post(id: int) -> Post:
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
            WHERE post_id = {id};"""
            cursor.execute(query)
            raw_data = list(cursor.fetchall())

    result: Post = None
    if len(raw_data) > 0:
        entry = raw_data[0]
        result = Post(id=entry[post_id_ind],
                           parent_id=entry[parent_id_ind],
                           channel=entry[channel_ind],
                           username=entry[username_ind],
                           timestamp=entry[post_time_ind].strftime('%m/%d/%Y %I:%M:%S %p'),
                           title=entry[title_ind],
                           body=entry[body_ind],
                           replies=get_posts(entry[post_id_ind], entry[channel_ind]))

    return result

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
                           channel=entry[channel_ind],
                           username=entry[username_ind],
                           timestamp=entry[post_time_ind].strftime('%m/%d/%Y %I:%M:%S %p'),
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
    if username == None or username == "":
        username = "Anonymous"
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
            cursor.execute(query)
        connection.commit()

def make_channel(name: str, description: str):
    connection = pymysql.connect(host="localhost",
                                 user=LOCAL_USER,
                                 password=LOCAL_PASSWORD,
                                 database="BuzzTalk")
    with connection:
        with connection.cursor() as cursor:
            query = f"""INSERT INTO woodruff_channels 
            (name, description)
            VALUES
            ('{name}', '{description}')"""
            cursor.execute(query)
        connection.commit()

def trace_root(post: Post) -> int:
    while post.parent_id != 0:
        post = get_post(post.parent_id)
    return post.id

def sign_up(username: str):
    username_ind = 0
    connection = pymysql.connect(host="localhost",
                                 user=LOCAL_USER,
                                 password=LOCAL_PASSWORD,
                                 database="BuzzTalk")
    with connection:
        with connection.cursor() as cursor:
            query = f"""SELECT * FROM registry
            WHERE username='{username}';"""
            cursor.execute(query)
            raw_data = list(cursor.fetchall())

            if len(raw_data) == 0:
                query = f"""INSERT INTO registry 
                (username)
                VALUES
                ('{username}')"""
                cursor.execute(query)
        connection.commit()

@app.get("/", response_class=RedirectResponse)
def read_root():
    return "/channel/general"

@app.get("/channel/{channel_name}")
async def view_posts(channel_name: str, username: Annotated[str | None, Cookie()] = None):
    if channel_name == None:
        channel_name = "general"
    if channel_name not in get_channels():
        return HTMLResponse(status_code=404)
    db = get_posts(0, channel_name)
    return page_generator.generate_posts_page(db, channel_name, get_channels(), username = username)

@app.get("/post/{id}")
async def view_post(id: int, username: Annotated[str | None, Cookie()] = None):
    post: Post = get_post(id)
    if post == None:
        return HTMLResponse(status_code=404)
    return page_generator.generate_post_focus_page(post, post.channel, get_channels(), username = username)

@app.get("/make_channel", response_class=HTMLResponse)
async def get_channels_page(server: str = "woodruff", username: Annotated[str | None, Cookie()] = None):
    return page_generator.generate_channels_page(get_channels(), username = username)

@app.get("/sign_in", response_class=HTMLResponse)
async def get_sign_in_page(username: Annotated[str | None, Cookie()] = None):
    return page_generator.generate_sign_in_page(get_channels(), username)

@app.post("/api/posts")
def create_post(channel: str = None, title: str = Form(...), content: str = Form(...), username: Annotated[str | None, Cookie()] = None):
    make_post(0, username, title, content, channel)
    return RedirectResponse(url=f"/channel/{channel}", status_code=303)

@app.post("/api/reply")
def create_reply(reply_id: int, channel: str, reply: str = Form(...), username: Annotated[str | None, Cookie()] = None):
    make_post(reply_id, username, None, reply, channel)
    root_id = trace_root(get_post(reply_id))
    return RedirectResponse(url=f"/post/{root_id}", status_code=303)

@app.post("/api/channel")
def create_channel(name: str = Form(...), description: str = Form(...)):
    make_channel(name, description)
    return RedirectResponse(url="/make_channel", status_code=303)

@app.post("/api/sign_in")
def sign_in(username: str = Form(...)):
    sign_up(username)
    response = RedirectResponse(url="/sign_in", status_code=303)
    response.set_cookie(key="username", value=username)
    return response

@app.post("/api/sign_out")
def sign_out():
    response = RedirectResponse(url="/sign_in", status_code=303)
    response.delete_cookie(key="username")
    return response

@app.get("/logo")
def get_logo():
    return FileResponse("logo/BuzzTalkLogo.jpeg")