from urllib.parse import urlsplit
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