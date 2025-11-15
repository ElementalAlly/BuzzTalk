from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, ConfigDict
from typing import List

class Post(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    id: int
    parent_id: int
    username: str
    title: str
    body: str
    replies: []

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


def generate_posts_page(db: List[Post], channel: str):
    posts_html = ""
    for post in reversed(db):  # Show new posts at the top
        posts_html += traverse_post(post, 0, channel)

    with open("HTML_templates\\post_w_comments.txt") as f:
        html_content = f.read().format(channel = channel, posts_html = posts_html)
    return HTMLResponse(content=html_content, status_code=200)