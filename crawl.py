from urllib.parse import urlsplit


def normalize_url(url: str) -> str:
    parts = urlsplit(url)
    normal_url = f"{parts.netloc}{parts.path}"
    normal_url = normal_url.rstrip("/")
    return normal_url.lower()
