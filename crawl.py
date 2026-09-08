from urllib.parse import (
    urlsplit,
    urljoin,
    urlparse,
)
from bs4 import BeautifulSoup, Tag
from typing import TypedDict
import asyncio
import aiohttp

class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]

class AsyncCrawler:
    def __init__(self, base_url, max_concurrency, max_pages):
        self.base_url = base_url
        self.base_domain = urlsplit(base_url).netloc
        self.page_data = {}
        self.lock = asyncio.Lock()
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.session = None
        self.max_pages = max_pages
        self.should_stop = False

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def add_page_visit(self, normalized_url):
        async with self.lock:
            if normalized_url in self.page_data:
                return False
            if self.should_stop:
                return False
            if len(self.page_data) >= self.max_pages:
                self.should_stop = True
                print("Reached maximum number of pages to crawl.")
                return False
            self.page_data[normalized_url] = None
            return True

    async def get_html(self, url):
        try:
            async with self.session.get(url, headers={"User-Agent": "BootCrawler/1.0"}) as response:
                if response.status > 399:
                    print(f"Request failed with status code {response.status}: {response.reason}")
                    return None
                content_type = response.headers.get("content-type", "")
                if "text/html" not in content_type:
                    print(f"Expected content-type text/html, but received {content_type}")
                    return None
                return await response.text()
        except Exception as e:
            print(f"network error: {e}")
            return None

    async def crawl_page(self, current_url: str):
        if self.should_stop:
            return
        if urlparse(current_url).netloc != self.base_domain:
            return
        async with self.semaphore:
            current_normalized = normalize_url(current_url)
            if not await self.add_page_visit(current_normalized):
                return
            html = await self.get_html(current_url)
            if html is None:
                async with self.lock:
                    self.page_data.pop(current_normalized, None)
                    return
            print(f"getting html from: {current_normalized}")
            async with self.lock:
                self.page_data[current_normalized] = extract_page_data(html, current_url)
            next_urls = get_urls_from_html(html, self.base_url)
        await asyncio.gather(
            *(self.crawl_page(url) for url in next_urls),
            return_exceptions=True,
        )

    async def crawl(self):
        await self.crawl_page(self.base_url)
        return {key: value for key, value in self.page_data.items() if value is not None}

async def crawl_site_async(base_url: str, max_concurrency: int, max_pages: int):
    async with AsyncCrawler(base_url, max_concurrency, max_pages) as crawler:
        return await crawler.crawl()


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