from urllib.parse import (
    urlsplit,
    urljoin,
    urlparse,
)
from bs4 import BeautifulSoup, Tag
from typing import TypedDict
import requests

class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]


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

def extract_page_data(html: str, page_url: str) -> PageData:
    return {
        "url": page_url,
        "heading": get_heading_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url),
    }

def get_html(url):
    try:
        response = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"})
    except Exception as e:
            raise Exception(f"network error: {e}")
    
    if response.status_code > 399:
        raise Exception(f"Request failed with status code {response.status_code}: {response.reason}")

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type:
        raise Exception(f"Expected content-type text/html, but received {content_type}")
    
    return response.text

def crawl_page(base_url, current_url=None, page_data=None):
    if current_url is None:
        current_url = base_url
    if page_data is None:
        page_data = {}
    if urlparse(base_url).netloc != urlparse(current_url).netloc:
        return page_data
    current_normalized = normalize_url(current_url)
    if current_normalized in page_data:
        return page_data
    html = get_html(current_url)
    print(f"getting html from: {current_normalized}")
    page_data[current_normalized] = (extract_page_data(html, current_url))
    for url in get_urls_from_html(html, base_url):
        page_data = crawl_page(base_url, url, page_data)
    return page_data
