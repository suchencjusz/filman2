import requests
import aiohttp
import asyncio
import ujson

# https://www.filmweb.pl/api/v1/title/875647/info
# {
#     "title": "The Menu ",
#     "year": 2022,
#     "type": "film",
#     "subType": "film_cinema",
#     "posterPath": "/56/47/875647/8053539.$.jpg"
# }

# https://www.filmweb.pl/api/v1/film/1212/rating
# count	332783
# rate	7.02568
# countWantToSee	12536
# countVote1	2595
# countVote2	2834
# countVote3	7237
# countVote4	13054
# countVote5	26087
# countVote6	54155
# countVote7	94523
# countVote8	76911
# countVote9	30347
# countVote10	25040


class Scraper:
    def __init__(self, headers=None, movie_id=None, endpoint_url=None):
        self.headers = headers
        self.movie_id = movie_id
        self.endpoint_url = endpoint_url

    async def fetch(self, session, url):
        async with session.get(url) as response:
            return await response.text()

    async def scrap(self):
        async with aiohttp.ClientSession() as session:
            info_url = f"https://www.filmweb.pl/api/v1/title/{self.movie_id}/info"
            rating_url = f"https://www.filmweb.pl/api/v1/film/{self.movie_id}/rating"

            info_task = asyncio.ensure_future(self.fetch(session, info_url))
            rating_task = asyncio.ensure_future(self.fetch(session, rating_url))

            responses = await asyncio.gather(info_task, rating_task)

            info_data = ujson.loads(responses[0])
            rating_data = ujson.loads(responses[1])

            title = info_data.get("title", None)
            year = int(info_data.get("year", None))
            poster_url = info_data.get("posterPath", None)
            community_rate = rating_data.get("rate", None)

            if title is None or year is None or poster_url is None:
                return False

            return await self.update_data(
                self.movie_id,
                title,
                year,
                poster_url,
                community_rate,
            )

    async def update_data(self, movie_id, title, year, poster_url, community_rate):
        r = requests.get(
            f"{self.endpoint_url}/movie/update?id={movie_id}&title={title}&year={year}&poster_url={poster_url}&community_rate={community_rate}"
        )

        if r.status_code != 200:
            return False

        return True
