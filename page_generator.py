from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, ConfigDict
from typing import List

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

def page_w_content(content: str, channels: List[str], username: str = ""):
    channel_list = ""
    for channel in channels:
        channel_list += f"<a href='/channel/{channel}'>{channel}</a>"
    if username == None or username == "":
        login_status = "Not signed in"
        logout_visible = "none"
    else:
        login_status = f"Signed in as: {username}"
        logout_visible = "blocked"
    with open("HTML_templates\\base.txt") as f:
        html_content = f.read().format(content = content, channels = channel_list, login_status = login_status, logout_visible = logout_visible)
    return HTMLResponse(content=html_content, status_code=200)

def traverse_post(post: Post, layer: int, channel: str):
    result = ""
    with open("HTML_templates\\reply_post.txt") as f:
        result = f.read().format(id = post.id, body = post.body, channel = channel, username = post.username, timestamp = post.timestamp)
    for i in range(len(post.replies)):
        result = result + traverse_post(post.replies[i], layer + 1, channel)
    
    result  = result + "</div>"
    return result

def process_channel(channel: str):
    with open("HTML_templates\\channel_listing.txt") as f:
        result = f.read().format(channel = channel)
    return result

def generate_posts_page(db: List[Post], channel: str, channels: List[str], username: str = None):
    posts_html = ""
    for post in reversed(db):  # Show new posts at the top
        with open("HTML_templates\\main_post.txt") as f:
            posts_html += f.read().format(username = post.username, timestamp = post.timestamp, id = post.id, title = post.title, body = post.body)

    with open("HTML_templates\\post_w_comments.txt") as f:
        page_content = f.read().format(channel = channel, posts_html = posts_html)
    return page_w_content(page_content, channels=channels, username = username)

def generate_channels_page(channels: List[str], server: str = "woodruff", username: str = None):
    channels_html = ""
    for channel in channels:
        channels_html += process_channel(channel)

    with open("HTML_templates\\make_channel.txt") as f:
        page_content = f.read().format(server = server, channels_html = channels_html)
    return page_w_content(page_content, channels = channels, username = username)

def generate_post_focus_page(post: Post, channel: str, channels: List[str], username: str = None):
    with open("HTML_templates\\post_focus.txt") as f:
        page_content = f.read()
    
    posts_html = ""
    for _post in reversed(post.replies):
        posts_html = posts_html + traverse_post(_post, 1, channel)
    page_content = page_content.format(title = post.title, id = post.id, username = post.username, timestamp = post.timestamp, body=post.body, channel=channel, posts_html=posts_html)

    return page_w_content(page_content, channels = channels, username = username)

def generate_sign_in_page(channels: List[str], username: str = None):
    if username == None:
        status = "Not signed in."
    else:
        status = f"Currently signed in as: {username}"
    with open("HTML_templates\\sign_in.txt") as f:
        page_content = f.read().format(status = status)
    return page_w_content(page_content, channels, username)