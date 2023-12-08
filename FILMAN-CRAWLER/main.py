import requests
import asyncio
import ujson

from fake_useragent import UserAgent

from tasks.scrap_movie import Scraper as scrap_movie

CORE_ENDPOINT = "http://localhost:8000"

HEADERS = {
    "User-Agent": UserAgent().random,
    "x-locale": "pl_PL",
    "Host": "www.filmweb.pl",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Origin": "https://www.filmweb.pl",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Sec-GPC": "1",
    "TE": "trailers",
}

async def main():
    worker1 = await scrap_movie(headers=HEADERS, movie_id=1212, endpoint_url=CORE_ENDPOINT).scrap()

if __name__ == "__main__":
    asyncio.run(main())

