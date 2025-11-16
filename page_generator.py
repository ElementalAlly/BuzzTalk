from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, ConfigDict
from typing import List

class Post(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: int
    parent_id: int
    channel: str
    username: str
    title: str
    body: str
    replies: []

def page_w_content(content: str, channels: List[str]):
    channel_list = ""
    for channel in channels:
        channel_list += f"<a href='/channel/{channel}'>{channel}</a>"
    with open("HTML_templates\\base.txt") as f:
        html_content = f.read().format(content = content, channels = channel_list)
    return HTMLResponse(content=html_content, status_code=200)

def traverse_post(post: Post, layer: int, channel: str):
    result = ""
    if layer == 0:
        with open("HTML_templates\\main_post.txt") as f:
            result = f.read().format(title = post.title, id = post.id, layer = layer, body = post.body, channel = channel)
    else:
        with open("HTML_templates\\reply_post.txt") as f:
            result = f.read().format(id = post.id, layer = layer, body = post.body, channel = channel)
    for i in range(len(post.replies)):
        result = result + traverse_post(post.replies[i], layer + 1, channel)
    
    result  = result + "</div>"
    return result

def process_channel(channel: str):
    with open("HTML_templates\\channel_listing.txt") as f:
        result = f.read().format(channel = channel)
    return result

def generate_posts_page(db: List[Post], channel: str, channels: List[str]):
    posts_html = ""
    for post in reversed(db):  # Show new posts at the top
        posts_html += traverse_post(post, 0, channel)

    with open("HTML_templates\\post_w_comments.txt") as f:
        page_content = f.read().format(channel = channel, posts_html = posts_html)
    return page_w_content(page_content, channels=channels)

def generate_channels_page(channels: List[str], server: str = "woodruff"):
    channels_html = ""
    for channel in channels:
        channels_html += process_channel(channel)

    with open("HTML_templates\\make_channel.txt") as f:
        page_content = f.read().format(server = server, channels_html = channels_html)
    return page_w_content(page_content, channels = channels)

def generate_post_focus_page(post: Post, channel: str, channels: List[str]):
    with open("HTML_templates\\post_focus.txt") as f:
        page_content = f.read()
    
    posts_html = ""
    for _post in reversed(post.replies):
        posts_html = posts_html + traverse_post(_post, 1, channel)
    page_content = page_content.format(title = post.title, id = post.id, body=post.body, channel=channel, posts_html=posts_html)

    return page_w_content(page_content, channels = channels)