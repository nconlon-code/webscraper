import sys
import asyncio
from crawl import crawl_site_async

async def main():
    if len(sys.argv) < 4:
        print("a website, max concurrency, and max pages must be provided")
        sys.exit(1)
    if len(sys.argv) > 4:
        print("too many arguments provided")
        sys.exit(1)
    base_url = sys.argv[1]
    max_concurrency = int(sys.argv[2])
    max_pages = int(sys.argv[3])
    print(f"starting crawl of: {sys.argv[1]}")
    page_data = await crawl_site_async(base_url, max_concurrency, max_pages)
    print(f"Found {len(page_data)} pages:")
    for page in page_data.values():
        print(f"- {page['url']}: {len(page['outgoing_links'])} outgoing links")

if __name__ == "__main__":
    asyncio.run(main())
