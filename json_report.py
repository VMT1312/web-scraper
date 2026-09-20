import json

from crawl import PageData


def write_json_report(page_data: dict[str, PageData], filename="report.json"):
    pages = list(page_data.values())
    pages.sort(key=lambda x: x["url"])
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(pages, f, indent=2)
