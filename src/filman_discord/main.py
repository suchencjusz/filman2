import os
from datetime import datetime

import logging

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


@tasks.task(s=10, auto_start=True, pass_app=True)
async def notifications_task(app: lightbulb.BotApp) -> None:
    def filmweb_movie_url_generator(movie_title: str, movie_year: int, movie_id: int) -> str:
        movie_title = movie_title.replace(" ", "+")
        return f"https://www.filmweb.pl/film/{movie_title}-{movie_year}-{movie_id}"

    def start_emoji_counter(stars: float) -> str:
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
            await rest.create_message(channel_id, embed=embed, content=f"<@{discord_id}>")
            # await rest.create_message(channel=channel_id, content=f"<@{discord_id}>")

            # async with bot.d.client_session.get(f"http://filman_server:8000/tasks/update/status/{id_task}/done") as resp:
            #     if not resp.ok:
            #         print(f"Error updating task status: {resp.status} {resp.reason}")

        except hikari.NotFoundError:
            print("Guild or channel not found.")
        except hikari.BadRequestError as e:
            print(f"Error sending message: {e}")

    async with bot.d.client_session.get(
        "http://filman_server:8000/tasks/get/to_do?task_types=send_discord_notification"
    ) as resp:
        if not resp.ok:
            return

        tasks = await resp.json()

        logging.info(f"Found {len(tasks)} tasks to do") #  found 7 len 
        logging.debug(f"Tasks: {tasks}")

        for task in tasks:
            if task["type"] == "send_discord_notification": # TODO fix task type
                filmweb_id = task["task_job"].split(",")[0]
                media_type = task["task_job"].split(",")[1]
                movie_id = task["task_job"].split(",")[2]

                if media_type == "movie":
                    async with bot.d.client_session.get(
                        f"http://filman_server:8000/filmweb/user/watched/movies/get?filmweb_id={filmweb_id}&movie_id={movie_id}"
                    ) as resp:
                        if not resp.ok:
                            return

                        user_id = 0
                        message_destinations = []

                        async with bot.d.client_session.get(
                            f"http://filman_server:8000/users/get?filmweb_id={filmweb_id}"
                        ) as resp:
                            if not resp.ok:
                                return

                            user = await resp.json()
                            user_id = user["id"]

                        async with bot.d.client_session.get(
                            f"http://filman_server:8000/users/get_all_channels?user_id={user_id}"
                        ) as resp:
                            if not resp.ok:
                                return

                            message_destinations = await resp.json()

                        data = await resp.json()

                        movie = data["movie"]

                        filmweb_id = data["filmweb_id"]
                        date_watched = data["date"]
                        rate = data["rate"]
                        comment = data["comment"]
                        favorite = data["favorite"]

                        movie_url = filmweb_movie_url_generator(movie["title"], movie["year"], movie["id"])

                        movie["poster_uri"] = "https://fwcdn.pl/fpo" + movie["poster_uri"]

                        embed = hikari.Embed(
                            title=f"{movie['title']}",
                            colour=0xFFC200,
                            url=movie_url,
                            timestamp=datetime.now().astimezone(),
                        )

                        embed.set_thumbnail(movie["poster_uri"])

                        embed.add_field(
                            name="Tytuł",
                            value=f"{movie['title']}",
                            inline=True,
                        )

                        embed.add_field(
                            name="Rok",
                            value=f"{movie['year']}",
                            inline=True,
                        )

                        if favorite:
                            embed.add_field(
                                name="Ulubiony",
                                value=f"❤️ Tak",
                                inline=True,
                            )

                        if comment:
                            embed.add_field(
                                name="Komentarz",
                                value=f"{comment}",
                                inline=True,
                            )

                        if rate:
                            embed.add_field(
                                name=f"Ocena `{filmweb_id}`",
                                value=f"{start_emoji_counter(rate)}",
                                inline=False,
                            )
                        else:
                            embed.add_field(
                                name=f"Ocena `{filmweb_id}`",
                                value=f"_brak oceny_",
                                inline=False,
                            )

                        embed.add_field(
                            name="Ocena społeczności",
                            value=f"{start_emoji_counter(movie['community_rate'])}",
                            inline=False,
                        )

                        for message_destination in message_destinations:
                            await send_discord_message(
                                app,
                                message_destination,
                                embed,
                                user_id,
                            )


bot.load_extensions_from("./endpoints/")

if __name__ == "__main__":
    bot.run()
