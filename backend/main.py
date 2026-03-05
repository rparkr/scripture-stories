# /// script
# dependencies = [
#   "fastapi",
#   "uvicorn",
#   "httpx",
#   "beautifulsoup4",
# ]
# ///

import re
import socket

import httpx
import uvicorn
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

BASE_URL = "https://www.churchofjesuschrist.org"

# Mapping of volumes to their URL paths
VOLUMES = {
    "old-testament": "/study/manual/old-testament-stories-2022",
    "new-testament": "/study/manual/new-testament-stories-2026",
    "book-of-mormon": "/study/manual/book-of-mormon-stories-2024",
    "doctrine-and-covenants": "/study/manual/doctrine-and-covenants-stories-2025",
}


class LocalIP:
    """Singleton class that computes and caches the local IP address."""

    _instance = None
    _ip: str

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._ip = cls._compute_ip()
        return cls._instance

    @staticmethod
    def _compute_ip() -> str:
        """Get local IP address by attempting to connect to a remote socket."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"
        finally:
            s.close()
        return ip

    def __str__(self) -> str:
        return self._ip

    def __repr__(self) -> str:
        return self._ip


# Singleton instance created at module load time
LOCAL_IP = LocalIP()


# Configure CORS for GitHub Pages and local development
allowed_origins = [
    "http://localhost:3000",  # Local frontend development
    "http://localhost:8000",  # Local testing
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    str(LOCAL_IP),
    "https://rparkr.github.io",  # GitHub Pages domain
    "https://rparkr.github.io/scripture-stories",  # GitHub Pages repo
]

# Remove None values (from get_local_ip edge cases)
allowed_origins = [origin for origin in allowed_origins if origin]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=False,
)


async def fetch_page(url: str):
    async with httpx.AsyncClient(follow_redirects=True) as client:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Page not found")
        return response.text


@app.get("/api/stories")
async def get_stories(volume: str = "new-testament"):
    if volume not in VOLUMES:
        raise HTTPException(status_code=400, detail="Invalid volume selected")

    toc_path = VOLUMES[volume]
    html = await fetch_page(BASE_URL + toc_path + "?lang=eng")
    soup = BeautifulSoup(html, "html.parser")
    stories = []

    links = soup.select("nav.manifest ul li a")
    for link in links:
        href = link.get("href")
        if href and toc_path in href:
            title_el = link.select_one("h4 p.title")
            title = title_el.get_text(strip=True) if title_el else ""

            subtitle_el = link.select_one("p.description")
            subtitle = subtitle_el.get_text(strip=True) if subtitle_el else ""

            scripture_el = link.select_one("h6 p.primaryMeta")
            scripture_ref = scripture_el.get_text(strip=True) if scripture_el else ""

            if title:
                stories.append(
                    {
                        "title": title,
                        "subtitle": subtitle,
                        "scripture_ref": scripture_ref,
                        "url": f"{BASE_URL}{href}" if href.startswith("/") else href,
                    }
                )
    return stories


@app.get("/api/content")
async def get_story_content(url: str):
    html = await fetch_page(url)
    soup = BeautifulSoup(html, "html.parser")
    slides = []

    content_container = soup.select_one(".body-block") or soup.select_one("article")
    if not content_container:
        raise HTTPException(status_code=404, detail="Story content not found")

    img_elements = content_container.find_all("img")

    for img in img_elements:
        parent_div = img.find_parent("div", class_=re.compile(r"imageWrapper"))
        parent_div = parent_div.find_parent("div") if parent_div else None
        if not parent_div:
            continue

        src = img.get("src") or (
            # srcset is a comma-delimited list of URLs like: "<img_url> 60w,<img url> 100w,<img_url> 200w,"
            # We want the last one (largest size).
            img.get("srcset", "").split(",")[-1].split(" ")[0]
            if img.get("srcset")
            else None
        )
        if not src:
            continue
        if src.startswith("//"):
            src = f"https:{src}"

        # Standardize on high-res images (the !1600 width is configurable). Any
        # size greater than the image's max width will return the full image.
        src = re.sub(
            pattern=r"^(.*)full/.*/0/default(.*)$",
            repl=r"\1full/!1600,/0/default\2",
            string=str(src),
        )

        caption_text = ""
        scripture_links = []

        current = parent_div.find_next_sibling()
        while current:
            if current.name == "div":
                break

            if current.name == "p" and current.has_attr("data-aid"):
                s_links = current.find_all("a", class_="scripture-ref")
                c_links = current.find_all("a", class_="cross-ref")
                all_links = s_links + c_links
                for sl in all_links:
                    scripture_links.append(
                        {
                            "text": sl.get_text(strip=True),
                            "url": (
                                f"{BASE_URL}{sl.get('href')}"
                                if sl.get("href", "").startswith("/")
                                else sl.get("href")
                            ),
                        }
                    )
                if not all_links:
                    p_text = current.get_text(" ", strip=True)
                    if p_text:
                        caption_text += " " + p_text

            current = current.find_next_sibling()
            if current and current.name == "footer":
                break

        slides.append(
            {
                "image": src,
                "alt_text": img.get("alt", ""),
                "caption": caption_text.strip(),
                "scripture_links": scripture_links,
                "is_intro": False,
            }
        )

    return {"slides": slides, "source_url": url}


@app.get("/")
async def serve_index():
    return FileResponse("../docs/index.html")


def main():
    app.mount("/", StaticFiles(directory="../docs"), name="static")
    print(
        f"\n📖 Scripture Stories app is now running\n👉 Go to: http://{LOCAL_IP}:8000\n"
    )
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
