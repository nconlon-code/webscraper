from urllib.parse import (
    urlsplit,
    urljoin,
)
from bs4 import BeautifulSoup, Tag


def normalize_url(url):
    splitUrl = urlsplit(url)
    cleaned = splitUrl.path.rstrip("/")
    normalized = f"{splitUrl.netloc}{cleaned}"
    return normalized.lower()

def get_heading_from_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    h_tag = soup.find("h1") or soup.find("h2")
    return h_tag.get_text(strip=True) if isinstance(h_tag, Tag) else ""

def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')
    search_area = soup.find("main") or soup
    p_tag = search_area.find("p")
    return p_tag.get_text(strip=True) if isinstance(p_tag, Tag) else ""

def get_urls_from_html(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    urls = []
    for link in soup.find_all("a"):
        href = link.get("href")
        if href is not None:
            full_url = urljoin(base_url, href)
            urls.append(full_url)
    return urls

def get_images_from_html(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    images = []
    for link in soup.find_all("img"):
        img = link.get("src")
        if img is not None:
            full_url = urljoin(base_url, img)
            images.append(full_url)
    return images
