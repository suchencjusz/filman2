import datetime
import logging
import os
import sys
import textwrap

import aiohttp
import hikari
import lightbulb
from lightbulb.ext import tasks

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logging.getLogger("lightbulb").setLevel(LOG_LEVEL)
logging.getLogger("hikari").setLevel(LOG_LEVEL)

if DISCORD_TOKEN == None or DISCORD_TOKEN == "": # todo check this
    logging.error("Provide DISCORD_TOKEN!")
    exit(-1)

bot = lightbulb.BotApp(
    DISCORD_TOKEN,
    intents=hikari.Intents.ALL,
    banner=None,
)

tasks.load(bot)


@bot.listen()
async def on_starting(_: hikari.StartingEvent) -> None:
    bot.d.client_session = aiohttp.ClientSession()
    bot.d.rest = bot.rest


@bot.listen()
async def on_stopping(_: hikari.StoppingEvent) -> None:
    await bot.d.client_session.close()


@tasks.task(s=10, auto_start=True, pass_app=True)
async def presence(app: lightbulb.BotApp) -> None:

    await app.update_presence(
        status=hikari.Status.ONLINE,
        activity=hikari.Activity(
            name="/filmweb me",
            type=hikari.ActivityType.COMPETING,
        ),
    )


@tasks.task(s=2, auto_start=True, pass_app=True, max_consecutive_failures=9999) # test and refactor this is sometime
async def notifications_task(app: lightbulb.BotApp) -> None:
    def filmweb_movie_url_generator(movie_title: str, movie_year: int, movie_id: int) -> str:
        movie_title = movie_title.replace(" ", "+")
        return f"https://www.filmweb.pl/film/{movie_title}-{movie_year}-{movie_id}"

    def star_emoji_counter(stars: float) -> str:
        """
        Convert float rating to emoji string.

        :param stars: float rating

        :return: emoji string
        """

        return_string = ""
        stars_int = int(stars)
        stars = float(stars)

        full = "🌕"
        near_full = "🌖"
        half = "🌗"
        near_zero = "🌘"
        zero = "🌑"

        t = 10 - stars_int

        for i in range(0, stars_int):
            return_string += full

        difference = stars - float(stars_int)

        if difference >= 0.7:
            return_string += near_full
            t = t - 1
        elif difference >= 0.3:
            return_string += half
            t = t - 1
        elif difference > 0:
            return_string += near_zero
            t = t - 1

        for i in range(0, t):
            return_string += zero

        return return_string

    def parse_rate(rate: int) -> str:
        if rate is not None and rate != 0:
            return star_emoji_counter(rate) + f" **{rate}/10**"
        return "_brak oceny_"

    def parse_movie_rate(rate: int, rate_type: str) -> str:  # refactor
        if rate is not None:
            return star_emoji_counter(rate) + f" **{round(rate, 1)}/10**"
        return f"_brak ocen {rate_type}_"

    def parse_series_rate(rate: int, rate_type: str) -> str:  # refactor
        if rate is not None:
            return star_emoji_counter(rate) + f" **{round(rate, 1)}/10**"
        return f"_brak ocen {rate_type}_"

    async def send_discord_message(
        app: lightbulb.BotApp,
        channel_id: int,
        embed: hikari.Embed,
        discord_id: int,
    ) -> None:
        rest = app.rest

        try:
            await rest.create_message(channel_id, embed=embed, user_mentions=discord_id)
        except hikari.NotFoundError:
            logging.info(f"Channel {channel_id} not found")
        except hikari.BadRequestError as e:
            logging.error(f"Error sending message: {e.status_code} {e.message}")

    async def send_discord_notification_watched(
        app: lightbulb.BotApp,
        filmweb_id: int,
        media_type: str,
        media_id: int,
    ) -> None:

        task_id = task["task_id"]

        if media_type == "movie":
            async with bot.d.client_session.get(
                f"http://filman_server:8000/filmweb/user/watched/movies/get?filmweb_id={filmweb_id}&movie_id={media_id}"
            ) as resp2:
                if not resp2.ok:
                    return

                logging.info(f"send_discord_notification_watched_movie {filmweb_id} {media_type} {media_id}")
                logging.info(f"sending notification for {filmweb_id} {media_id}")

                user_id = 0
                message_destinations = []

                async with bot.d.client_session.get(f"http://filman_server:8000/users/get?filmweb_id={filmweb_id}") as resp:
                    if not resp.ok:
                        return

                    user = await resp.json()
                    user_id = user["id"]
                    discord_id = user["discord_id"]

                async with bot.d.client_session.get(
                    f"http://filman_server:8000/users/get_all_channels?user_id={user_id}"
                ) as resp3:
                    if not resp3.ok:
                        return

                    message_destinations = await resp3.json()

                data = await resp2.json()

                movie = data["movie"]

                filmweb_id = data["filmweb_id"]
                date_watched = data["date"]
                rate = data["rate"]
                comment = data["comment"]
                favorite = data["favorite"]

                # parse data to none-safe
                date_watched = datetime.datetime.fromisoformat(date_watched).astimezone(tz=datetime.timezone.utc)
                comment = "\n".join(textwrap.wrap(comment, width=62)) if comment is not None else None
                movie_url = filmweb_movie_url_generator(movie["title"], movie["year"], movie["id"])
                movie["poster_url"] = (
                    "https://fwcdn.pl/fpo" + movie["poster_url"]
                    if movie["poster_url"] is not None
                    else "https://vectorified.com/images/no-data-icon-23.png"
                )

                rate_parsed_star = ""

                rate_parsed_star = parse_rate(rate)
                social_rate_parsed_star = parse_movie_rate(movie["community_rate"], "społeczności")
                critcis_rate_parsed_star = parse_movie_rate(movie["critics_rate"], "krytyków")

                embed1 = hikari.Embed(
                    title=f"{movie['title']} ({movie['year']})",
                    description=f"<@{discord_id}>",
                    url=movie_url,
                    colour=0xFFC200,
                    timestamp=date_watched,
                )
                embed1.set_thumbnail(movie["poster_url"])

                if favorite:
                    rate_parsed_star += " :heart:"

                embed1.add_field(
                    name=f"Ocena `{filmweb_id}`",
                    value=rate_parsed_star,
                    inline=False,
                )

                if comment:
                    embed1.add_field(
                        name="Komentarz",
                        value=comment,
                        inline=False,
                    )

                embed1.add_field(
                    name="Ocena społeczności",
                    value=social_rate_parsed_star,
                    inline=False,
                )

                embed1.add_field(
                    name="Ocena krytyków",
                    value=critcis_rate_parsed_star,
                    inline=False,
                )

                for message_destination in message_destinations:
                    await send_discord_message(
                        app,
                        message_destination,
                        embed1,
                        discord_id,
                    )

        if media_type == "series":
            async with bot.d.client_session.get(
                f"http://filman_server:8000/filmweb/user/watched/series/get?filmweb_id={filmweb_id}&series_id={media_id}"
            ) as resp2:
                if not resp2.ok:
                    return

                logging.info(f"send_discord_notification_watched_series {filmweb_id} {media_type} {media_id}")
                logging.info(f"sending notification for {filmweb_id} {media_id}")

                user_id = 0
                message_destinations = []

                async with bot.d.client_session.get(f"http://filman_server:8000/users/get?filmweb_id={filmweb_id}") as resp:
                    if not resp.ok:
                        return

                    user = await resp.json()
                    user_id = user["id"]
                    discord_id = user["discord_id"]

                async with bot.d.client_session.get(
                    f"http://filman_server:8000/users/get_all_channels?user_id={user_id}"
                ) as resp3:
                    if not resp3.ok:
                        return

                    message_destinations = await resp3.json()

                data = await resp2.json()

                series = data["series"]

                filmweb_id = data["filmweb_id"]
                date_watched = data["date"]
                rate = data["rate"]
                comment = data["comment"]
                favorite = data["favorite"]

                # parse data to none-safe
                date_watched = datetime.datetime.fromisoformat(date_watched).astimezone(tz=datetime.timezone.utc)
                comment = "\n".join(textwrap.wrap(comment, width=62)) if comment is not None else None
                series_url = filmweb_movie_url_generator(series["title"], series["year"], series["id"])
                series["poster_url"] = (
                    "https://fwcdn.pl/fpo" + series["poster_url"]
                    if series["poster_url"] is not None
                    else "https://vectorified.com/images/no-data-icon-23.png"
                )

                rate_parsed_star = ""

                rate_parsed_star = parse_rate(rate)
                social_rate_parsed_star = parse_series_rate(series["community_rate"], "społeczności")
                critcis_rate_parsed_star = parse_series_rate(series["critics_rate"], "krytyków")

                series_title = ""
                series_title = (
                    f"{series['title']} ({series['year']})"
                    if series["other_year"] is None
                    else f"{series['title']} ({series['year']} - {series['other_year']})"
                )

                embed1 = hikari.Embed(
                    title=series_title,
                    description=f"<@{discord_id}>",
                    url=series_url,
                    colour=0x00FFC3,
                    timestamp=date_watched,
                )
                embed1.set_thumbnail(series["poster_url"])

                if favorite:
                    rate_parsed_star += " :heart:"

                embed1.add_field(
                    name=f"Ocena `{filmweb_id}`",
                    value=rate_parsed_star,
                    inline=False,
                )

                if comment:
                    embed1.add_field(
                        name="Komentarz",
                        value=comment,
                        inline=False,
                    )

                embed1.add_field(
                    name="Ocena społeczności",
                    value=social_rate_parsed_star,
                    inline=False,
                )

                embed1.add_field(
                    name="Ocena krytyków",
                    value=critcis_rate_parsed_star,
                    inline=False,
                )

                for message_destination in message_destinations:
                    await send_discord_message(
                        app,
                        message_destination,
                        embed1,
                        discord_id,
                    )

        async with bot.d.client_session.get(f"http://filman_server:8000/tasks/update/status/{task_id}/completed") as resp:
            if not resp.ok:
                print(f"Error updating task status: {resp.status} {resp.reason}")

    async with bot.d.client_session.get(
        "http://filman_server:8000/tasks/get/to_do?task_types=send_discord_notification"
    ) as resp:
        if not resp.ok:
            if resp.status == 404:
                logging.info("No tasks to do")
                return

            logging.error(f"Error getting tasks: {resp.status} {resp.reason}")
            return

        task = await resp.json()

        logging.info(task)

        if task["task_type"] == "send_discord_notification":  # divide it to other funtion

            filmweb_id = task["task_job"].split(",")[0]
            media_type = task["task_job"].split(",")[1]
            media_id = task["task_job"].split(",")[2]

            await send_discord_notification_watched(
                bot,
                filmweb_id,
                media_type,
                media_id,
            )


bot.load_extensions_from("./endpoints/")

if __name__ == "__main__":
    bot.run()
