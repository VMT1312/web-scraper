from urllib.parse import urlsplit, urljoin
from bs4 import BeautifulSoup, Tag
from typing import TypedDict
import requests


class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]


def normalize_url(url: str) -> str:
    parts = urlsplit(url)
    normal_url = f"{parts.netloc}{parts.path}"
    normal_url = normal_url.rstrip("/")
    return normal_url.lower()


def get_heading_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    h_tag = soup.find("h1")
    if not h_tag:
        h_tag = soup.find("h2")

    return h_tag.get_text(strip=True) if isinstance(h_tag, Tag) else ""


def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    main_section = soup.find("main")
    if isinstance(main_section, Tag):
        first_p = main_section.find("p")
    else:
        first_p = soup.find("p")
    return first_p.get_text(strip=True) if isinstance(first_p, Tag) else ""


def get_urls_from_html(html: str, base_url: str) -> list[str]:
    urls = []

    soup = BeautifulSoup(html, "html.parser")
    a_tags = soup.find_all("a")
    for tag in a_tags:
        if not isinstance(tag, Tag):
            continue
        url = tag.get("href")
        if isinstance(url, str) and url:
            urls.append(urljoin(base_url, url))

    return urls


def get_images_from_html(html: str, base_url: str) -> list[str]:
    urls = []

    soup = BeautifulSoup(html, "html.parser")
    img_tags = soup.find_all("img")
    for tag in img_tags:
        if not isinstance(tag, Tag):
            continue
        path = tag.get("src")
        if isinstance(path, str) and path:
            urls.append(urljoin(base_url, path))

    return urls


def extract_page_data(html: str, page_url: str) -> PageData:
    return {
        "url": page_url,
        "heading": get_heading_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url),
    }


def get_html(
    url: str = "https://learnwebscraping.dev/practice/ecommerce/",
) -> bytes | str:
    res = requests.get(
        url,
        headers={
            "User-Agent": "BootCrawler/1.0",
        },
    )
    if res.status_code >= 400:
        raise Exception("error fetching data")
    content_type = res.headers.get("content-type", "")
    if "text/html" not in content_type:
        raise Exception(f"got non-HTML response: {content_type}")
    return res.content
