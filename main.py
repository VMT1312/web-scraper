import sys
from crawl import crawl_site_async
import asyncio


async def main():
    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    if len(sys.argv) > 2:
        print("too many arguments provided")
        sys.exit(1)
    print(f"starting crawl of: {sys.argv[1]}")
    page_data = await crawl_site_async(sys.argv[1], 10)
    for v in page_data.values():
        print(v)


if __name__ == "__main__":
    asyncio.run(main())
