from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
import glob
import markdown
from typing import List, Dict

app = FastAPI()

# Tell FastAPI where templates and static files live
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


def _get_posts_dir() -> str:
    return os.path.join(os.path.dirname(__file__), "content", "posts")


def list_posts() -> List[Dict]:
    """Scan the posts folder and return basic metadata for each markdown file."""
    posts = []
    posts_dir = _get_posts_dir()
    pattern = os.path.join(posts_dir, "*.md")
    for path in sorted(glob.glob(pattern), reverse=True):
        slug = os.path.splitext(os.path.basename(path))[0]
        with open(path, "r", encoding="utf8") as f:
            text = f.read()
        # first line starting with # is title
        title = None
        for line in text.splitlines():
            if line.strip().startswith("# "):
                title = line.strip().lstrip("# ")
                break
        if not title:
            title = slug.replace("-", " ").title()
        excerpt = text.strip().split("\n\n", 1)[0]
        if len(excerpt) > 200:
            excerpt = excerpt[:197].rsplit(" ", 1)[0] + "..."
        posts.append({"slug": slug, "title": title, "excerpt": excerpt})
    return posts


def load_post(slug: str) -> Dict:
    posts_dir = _get_posts_dir()
    path = os.path.join(posts_dir, f"{slug}.md")
    if not os.path.exists(path):
        raise FileNotFoundError
    with open(path, "r", encoding="utf8") as f:
        text = f.read()
    # render markdown to html
    html = markdown.markdown(text, extensions=["fenced_code", "tables"])
    # title extraction similar to list_posts
    title = None
    for line in text.splitlines():
        if line.strip().startswith("# "):
            title = line.strip().lstrip("# ")
            break
    if not title:
        title = slug.replace("-", " ").title()
    return {"slug": slug, "title": title, "html": html}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    projects = [
        {
            "title": "Database Automation Toolkit",
            "description": "Tools and scripts for automating database deployments, backups, and health checks.",
            "url": "#",
        },
        {
            "title": "Cloud Migration Scripts",
            "description": "Opinionated helpers to migrate on-prem databases to Azure with minimal downtime.",
            "url": "#",
        },
    ]
    recent_posts = list_posts()[:3]
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "name": "Surya Mishra",
            "tagline": "Refugee. Builder. Dreamer. Technologist.",
            "projects": projects,
            "recent_posts": recent_posts,
        },
    )


@app.get("/health")
async def health():
    """Simple health check for probes and CI."""
    return {"status": "ok"}


@app.get("/blog", response_class=HTMLResponse)
async def blog_index(request: Request):
    posts = list_posts()
    return templates.TemplateResponse("blog_list.html", {"request": request, "posts": posts})


@app.get("/blog/{slug}", response_class=HTMLResponse)
async def blog_post(request: Request, slug: str):
    try:
        post = load_post(slug)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Post not found")
    return templates.TemplateResponse("blog_post.html", {"request": request, "post": post})
