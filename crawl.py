from urllib.parse import urlsplit, urljoin
from bs4 import BeautifulSoup, Tag
from typing import TypedDict
import requests
import asyncio
import aiohttp
from urllib.parse import urlsplit


class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]


class AsyncCrawler:
    def __init__(
        self, base_url: str, base_domain: str, max_concurrency: int, max_pages: int
    ) -> None:
        self.base_url = base_url
        self.base_domain = base_domain
        self.page_data = {}
        self.visited = set()
        self.lock = asyncio.Lock()
        self.session = None
        self.max_concurrency = max_concurrency
        self.semaphore = asyncio.Semaphore(self.max_concurrency)
        self.max_pages = max_pages
        self.should_stop = False
        self.all_tasks = set()

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def add_page_visit(self, normalized_url: str):
        if self.should_stop:
            return False
        async with self.lock:
            if normalized_url in self.visited:
                return False
            if len(self.visited) == self.max_pages:
                self.should_stop = True
                print("Reached maximum number of pages to crawl.")
                return False
            self.visited.add(normalized_url)
            return True

    async def get_html(self, url: str) -> str | None:
        try:
            async with self.session.get(
                url, headers={"User-Agent": "BootCrawler/1.0"}
            ) as res:
                if res.status >= 400:
                    print("error fetching data")
                    return None
                content_type = res.headers.get("content-type", "")
                if "text/html" not in content_type:
                    print(f"got non-HTML response: {content_type}")
                    return None
                return await res.text()
        except Exception as e:
            print(f"error fetching data for {url}: {e}")
            return None

    async def crawl_page(
        self,
        current_url: str | None = None,
    ):
        try:
            if self.should_stop:
                return

            if current_url is None:
                current_url = self.base_url
            current_url_obj = urlsplit(current_url)
            if current_url_obj.netloc != self.base_domain:
                return

            normal_url = normalize_url(current_url)
            not_exist = await self.add_page_visit(normal_url)
            if not not_exist:
                return

            async with self.semaphore:
                print(f"crawling at: {normal_url}")
                html = await self.get_html(current_url)

                print(f"extracting page data at: {normal_url}")
                async with self.lock:
                    self.page_data[normal_url] = extract_page_data(html, self.base_url)

                for url in self.page_data[normal_url]["outgoing_links"]:
                    self.all_tasks.add(asyncio.create_task(self.crawl_page(url)))
        finally:
            self.all_tasks.discard(asyncio.current_task())

    async def crawl(self):
        self.all_tasks.add(asyncio.create_task(self.crawl_page(self.base_url)))
        while self.all_tasks:
            await asyncio.gather(*self.all_tasks)
        return self.page_data


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


async def crawl_site_async(
    base_url: str, max_concurrency: int, max_pages: int
) -> dict[str, PageData]:
    base_domain = urlsplit(base_url).netloc
    async with AsyncCrawler(
        base_url, base_domain, max_concurrency, max_pages
    ) as crawler:
        page_data = await crawler.crawl()
    return page_data
