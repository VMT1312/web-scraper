import sys
import asyncio
from crawl import crawl_site_async
from json_report import write_json_report


async def main():
    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    if len(sys.argv) > 4:
        print("too many arguments provided")
        sys.exit(1)
    print(f"starting crawl of: {sys.argv[1]}")
    page_data = await crawl_site_async(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
    write_json_report(page_data)


if __name__ == "__main__":
    asyncio.run(main())
