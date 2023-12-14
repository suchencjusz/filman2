import os
import hikari
import lightbulb
import aiohttp

from datetime import datetime

from lightbulb.ext import tasks


# bot = lightbulb.BotApp(
#     "MTE4MjM3MTY1ODM0NzA2NTM5NA.Gr7OHu.Y3PW4Dl98nLZAzAw1eJfvAzpushE3GXyM0qAX8",
#     intents=hikari.Intents.ALL,
#     banner=None,
# )

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
            name="/tracker me",
            type=hikari.ActivityType.COMPETING,
        ),
    )

@tasks.task(s=10, auto_start=True, pass_app=True)
async def notifications_task(app: lightbulb.BotApp) -> None:
    def filmweb_movie_url_generator(
        movie_title: str, movie_year: int, movie_id: int
    ) -> str:
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
        guild_id: int,
        channel_id: int,
        embed: hikari.Embed,
        discord_id: int,
        id_task: int,
    ) -> None:
        rest = app.rest

        try:
            # Send the embed to the specified channel in the specified guild
            await rest.create_message(
                channel_id, embed=embed, content=f"<@{discord_id}>"
            )
            # await rest.create_message(channel=channel_id, content=f"<@{discord_id}>")
            print(f"Embed sent to channel {channel_id} in guild {guild_id}.")

            async with bot.d.client_session.get(
                f"http://filman-server:8000/task/update?id_task={id_task}&status=done",
            ) as resp:
                if not resp.ok:
                    return

        except hikari.NotFoundError:
            print("Guild or channel not found.")
        except hikari.BadRequestError as e:
            print(f"Error sending message: {e}")

    allowed_tasks = ["send_discord"]

    async with bot.d.client_session.post(
        "http://filman-server:8000/tasks/get",
        json={
            "status": "waiting",
            "types": allowed_tasks,
        },
    ) as resp:
        if not resp.ok:
            return

        tasks = await resp.json()

        for task in tasks:
            if task["type"] == "send_discord":
                id_filmweb = task["job"].split(",")[0]
                movie_id = task["job"].split(",")[1]

                async with bot.d.client_session.get(
                    f"http://filman-server:8000/user/watched/film/get?id_filmweb={id_filmweb}&movie_id={movie_id}"
                ) as resp:
                    if not resp.ok:
                        return

                    data = await resp.json()

                    user_rate = data[0]
                    movie = data[1]
                    user_info = data[2]
                    destiantions_list = data[3]

                    #print everything from embedes
                    print("movie_title", movie["title"])
                    print("movie_year", movie["year"])
                    print("comment", user_rate["comment"])
                    print("favorite", user_rate["favorite"])
                    print("rate", user_rate["rate"])

                    movie_url = filmweb_movie_url_generator(
                        movie["title"], movie["year"], movie["id"]
                    )

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

                    if user_rate["favorite"] != 0:
                        embed.add_field(
                            name="Ulubiony",
                            value=f"❤️ Tak",
                            inline=True,
                        )

                    if user_rate["comment"]:
                        embed.add_field(
                            name="Komentarz",
                            value=f"{user_rate['comment']}",
                            inline=True,
                        )

                    if user_rate["rate"] != 0:
                        embed.add_field(
                            name=f"Ocena `{user_info['id_filmweb']}`",
                            value=f"{start_emoji_counter(user_rate['rate'])}",
                            inline=False,
                        )
                    else:
                        embed.add_field(
                            name=f"Ocena `{user_info['id_filmweb']}`",
                            value=f"_brak oceny_",
                            inline=False,
                        )

                    embed.add_field(
                        name="Ocena społeczności",
                        value=f"{start_emoji_counter(movie['community_rate'])}",
                        inline=False,
                    )

                    embed.set_footer(text=f"Filman • github/suchencjusz", icon=None)

                    for destination in destiantions_list:
                        await send_discord_message(
                            app,
                            destination[0],
                            destination[1],
                            embed,
                            user_info["id_discord"],
                            task["id_task"],
                        )


bot.load_extensions_from("./endpoints/")

if __name__ == "__main__":
    bot.run()
