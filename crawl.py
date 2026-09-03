from urllib.parse import urlsplit

def normalize_url(url):
    splitUrl = urlsplit(url)
    cleaned = splitUrl.path.rstrip("/")
    normalized = f"{splitUrl.netloc}{cleaned}"
    return normalized.lower()
