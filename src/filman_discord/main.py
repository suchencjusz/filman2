import datetime
import logging
import os
import textwrap

import aiohttp
import hikari
import lightbulb
from lightbulb.ext import tasks

bot = lightbulb.BotApp(
    os.environ.get("DISCORD_TOKEN"),
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


@tasks.task(s=2, auto_start=True, pass_app=True)
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
        if rate == 0 or rate is None:
            return "_brak oceny_"
        return star_emoji_counter(rate)

    def parse_movie_rate(rate: int, rate_type: str) -> str:
        if rate is not None:
            return star_emoji_counter(rate)
        return f"_brak ocen {rate_type}_"

    async def send_discord_message(
        app: lightbulb.BotApp,
        channel_id: int,
        embed: hikari.Embed,
        discord_id: int,
        id_task: int,
    ) -> None:
        rest = app.rest

        try:
            # Send the embed to the specified channel in the specified guild
            await rest.create_message(channel_id, embed=embed, user_mentions=discord_id)
            # await rest.create_message(channel=channel_id, content=f"<@{discord_id}>")

        except hikari.NotFoundError:
            print("Guild or channel not found.")
        except hikari.BadRequestError as e:
            print(f"Error sending message: {e}")

    async with bot.d.client_session.get(
        "http://filman_server:8000/tasks/get/to_do?task_types=send_discord_notification"
    ) as resp:
        if not resp.ok:
            return

        task = await resp.json()

        logging.info(task)

        if task["task_type"] == "send_discord_notification":
            task_id = task["task_id"]

            filmweb_id = task["task_job"].split(",")[0]
            media_type = task["task_job"].split(",")[1]
            movie_id = task["task_job"].split(",")[2]

            if media_type == "movie":
                async with bot.d.client_session.get(
                    f"http://filman_server:8000/filmweb/user/watched/movies/get?filmweb_id={filmweb_id}&movie_id={movie_id}"
                ) as resp2:
                    if not resp2.ok:
                        return

                    logging.info(f"sending notification for {filmweb_id} {movie_id}")

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

                    # parase data to none-safe
                    date_watched = datetime.datetime.fromisoformat(date_watched).astimezone(tz=datetime.timezone.utc)
                    comment = "\n".join(textwrap.wrap(comment, width=62)) if comment is not None else None
                    movie_url = filmweb_movie_url_generator(movie["title"], movie["year"], movie["id"])
                    movie["poster_url"] = (
                        "https://fwcdn.pl/fpo" + movie["poster_url"]
                        if movie["poster_url"] is not None
                        else "https://vectorified.com/images/no-data-icon-23.png"
                    )

                    rate_parsed = ""

                    rate_parsed = parse_rate(rate)
                    social_rate_parsed = parse_movie_rate(movie["community_rate"], "społeczności")
                    critcis_rate_parsed = parse_movie_rate(movie["critics_rate"], "krytyków")

                    embed1 = hikari.Embed(
                        title=f"{movie['title']} ({movie['year']})",
                        description=f"<@{discord_id}>",
                        url=movie_url,
                        colour=0xFFC200,
                        timestamp=date_watched,
                    )
                    embed1.set_thumbnail(movie["poster_url"])

                    user_rate_field = ""

                    if rate == 0 or rate is None:
                        user_rate_field = f"_brak oceny_ :heart: `{filmweb_id}`" if favorite else f"_brak oceny_ `{filmweb_id}`"
                    else:
                        user_rate_field = f"{rate}/10 :heart: `{filmweb_id}`" if favorite else f"{rate}/10 `{filmweb_id}`"

                    embed1.add_field(
                        name=user_rate_field,
                        value=rate_parsed,
                        inline=False,
                    )

                    if comment:
                        embed1.add_field(
                            name="Komentarz",
                            value=comment,
                            inline=False,
                        )

                    society_rate_field = ""

                    if movie["community_rate"] == 0 or movie["community_rate"] is None:
                        society_rate_field = "_brak ocen społeczności_"
                    else:
                        society_rate_field = f"{round(movie['community_rate'], 1)}/10 społeczność"

                    embed1.add_field(
                        name=society_rate_field,
                        value=social_rate_parsed,
                        inline=False,
                    )

                    critcis_rate_parsed = ""

                    if movie["critics_rate"] == 0 or movie["critics_rate"] is None:
                        critcis_rate_parsed = "_brak ocen krytyków_"
                    else:
                        critcis_rate_parsed = f"{round(movie['critics_rate'], 1)}/10 krytycy"

                    embed1.add_field(
                        name=critcis_rate_parsed,
                        value=critcis_rate_parsed,
                        inline=False,
                    )

                    for message_destination in message_destinations:
                        await send_discord_message(
                            app,
                            message_destination,
                            embed1,
                            discord_id,
                            task_id,
                        )

            async with bot.d.client_session.get(f"http://filman_server:8000/tasks/update/status/{task_id}/completed") as resp:
                if not resp.ok:
                    print(f"Error updating task status: {resp.status} {resp.reason}")


bot.load_extensions_from("./endpoints/")

if __name__ == "__main__":
    bot.run()
