import sys
import asyncio
from crawl import crawl_site_async

async def main():
    if len(sys.argv) < 2:
        print("no website provided")
        sys.exit(1)
    if len(sys.argv) > 2:
        print("too many arguments provided")
        sys.exit(1)
    print(f"starting crawl of: {sys.argv[1]}")
    page_data = await crawl_site_async(sys.argv[1])
    print(f"Found {len(page_data)} pages:")
    for page in page_data.values():
        print(f"- {page['url']}: {len(page['outgoing_links'])} outgoing links")

if __name__ == "__main__":
    asyncio.run(main())
