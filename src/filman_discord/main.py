import asyncio
import datetime
import logging
import os
import sys
import textwrap

import aiohttp
import hikari
import lightbulb
from lightbulb.ext import tasks

from filman_discord.utils.star_counter import star_emoji_counter

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN")

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logging.getLogger("lightbulb").setLevel(LOG_LEVEL)
logging.getLogger("hikari").setLevel(LOG_LEVEL)

if DISCORD_TOKEN == None or DISCORD_TOKEN == "":  # todo check this
    logging.error("Provide DISCORD_TOKEN!")
    exit(-1)

intents = hikari.Intents.GUILDS | hikari.Intents.GUILD_MESSAGES | hikari.Intents.MESSAGE_CONTENT

bot = lightbulb.BotApp( # to do: disable cache
    DISCORD_TOKEN,
    intents=intents,
    banner=None,
    cache_settings=hikari.impl.CacheSettings(
        components=hikari.impl.CacheComponents.NONE,
    ),
)

tasks.load(bot)


@bot.listen()
async def on_starting(_: hikari.StartingEvent) -> None:
    timeout = aiohttp.ClientTimeout(total=15, connect=5)
    bot.d.client_session = aiohttp.ClientSession(timeout=timeout)
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


@tasks.task(s=2, auto_start=True, pass_app=True, max_consecutive_failures=9999)  # test and refactor this is sometime
async def notifications_task(app: lightbulb.BotApp) -> None:
    def filmweb_media_url_generator(media_kind: str, title: str, year: int | None, media_id: int) -> str:
        safe_title = (title or str(media_id)).replace(" ", "+")
        return f"https://www.filmweb.pl/{media_kind}/{safe_title}-{year or ''}-{media_id}"

    def parse_rate(rate: int) -> str:
        if rate is not None and rate != 0:
            return star_emoji_counter(rate) + f" **{rate}/10**"
        return "_brak oceny_"

    def parse_media_rate(rate: float | None, rate_type: str) -> str:
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

    async def update_task_status(task_id: int, status: str) -> None:
        try:
            async with bot.d.client_session.get(
                f"http://filman_server:8000/tasks/update/status/{task_id}/{status}"
            ) as resp:
                if not resp.ok:
                    logging.error(f"Error updating task status: {resp.status} {resp.reason}")
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            logging.warning(f"Failed to update task {task_id} status to {status}: {exc}")

    async def send_discord_notification_watched(
        app: lightbulb.BotApp,
        task_id: int,
        filmweb_id: str,
        media_type: str,
        media_id: str,
    ) -> None:
        final_status = "completed"
        try:
            if media_type == "movie":
                watched_url = (
                    f"http://filman_server:8000/filmweb/user/watched/movies/get"
                    f"?filmweb_id={filmweb_id}&movie_id={media_id}"
                )
                media_key = "movie"
                url_kind = "film"
                embed_colour = 0xFFC200
            elif media_type == "series":
                watched_url = (
                    f"http://filman_server:8000/filmweb/user/watched/series/get"
                    f"?filmweb_id={filmweb_id}&series_id={media_id}"
                )
                media_key = "series"
                url_kind = "serial"
                embed_colour = 0x00FFC3
            else:
                logging.error(f"Unsupported notification media_type: {media_type}")
                final_status = "error"
                return

            async with bot.d.client_session.get(watched_url) as resp2:
                if not resp2.ok:
                    logging.warning(f"Watched {media_type} not found for {filmweb_id}/{media_id}: HTTP {resp2.status}")
                    return

                logging.info(f"send_discord_notification_watched_{media_type} {filmweb_id} {media_type} {media_id}")
                logging.info(f"sending notification for {filmweb_id} {media_id}")

                async with bot.d.client_session.get(
                    f"http://filman_server:8000/users/get?filmweb_id={filmweb_id}"
                ) as resp:
                    if not resp.ok:
                        logging.warning(f"User not found for {filmweb_id}: HTTP {resp.status}")
                        return

                    user = await resp.json()
                    user_id = user["id"]
                    discord_id = user["discord_id"]

                async with bot.d.client_session.get(
                    f"http://filman_server:8000/users/get_all_channels?user_id={user_id}"
                ) as resp3:
                    if not resp3.ok:
                        logging.info(f"No notification channels for user {user_id}: HTTP {resp3.status}")
                        return

                    message_destinations = await resp3.json()

                data = await resp2.json()

            media = data[media_key]
            filmweb_id = data["filmweb_id"]
            date_watched = datetime.datetime.fromisoformat(data["date"]).astimezone(tz=datetime.timezone.utc)
            rate = data["rate"]
            comment = data["comment"]
            favorite = data["favorite"]

            wrapped_comment = "\n".join(textwrap.wrap(comment, width=62)) if comment is not None else ""
            media_title = media.get("title") or f"ID {media['id']}"
            media_year = media.get("year")
            media_url = filmweb_media_url_generator(url_kind, media_title, media_year, media["id"])
            poster_url = (
                "https://fwcdn.pl/fpo" + media["poster_url"]
                if media.get("poster_url") is not None
                else "https://vectorified.com/images/no-data-icon-23.png"
            )

            rate_parsed_star = parse_rate(rate)
            social_rate_parsed_star = parse_media_rate(media.get("community_rate"), "społeczności")
            critics_rate_parsed_star = parse_media_rate(media.get("critics_rate"), "krytyków")

            if media_type == "series" and media.get("other_year") is not None:
                embed_title = f"{media_title} ({media_year} - {media['other_year']})"
            elif media_year is not None:
                embed_title = f"{media_title} ({media_year})"
            else:
                embed_title = media_title

            embed1 = hikari.Embed(
                title=embed_title,
                description=f"<@{discord_id}>",
                url=media_url,
                colour=embed_colour,
                timestamp=date_watched,
            )
            embed1.set_thumbnail(poster_url)

            if favorite:
                rate_parsed_star += " :heart:"

            embed1.add_field(
                name=f"Ocena `{filmweb_id}`",
                value=rate_parsed_star,
                inline=False,
            )

            if wrapped_comment:
                embed1.add_field(
                    name="Komentarz",
                    value=wrapped_comment,
                    inline=False,
                )

            embed1.add_field(
                name="Ocena społeczności",
                value=social_rate_parsed_star,
                inline=False,
            )

            embed1.add_field(
                name="Ocena krytyków",
                value=critics_rate_parsed_star,
                inline=False,
            )

            for message_destination in message_destinations:
                await send_discord_message(
                    app,
                    message_destination,
                    embed1,
                    discord_id,
                )
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            logging.warning(f"Network/timeout error processing notification task {task_id}: {exc}")
            final_status = "queued"
        except Exception as exc:
            logging.exception(f"Unexpected error processing notification task {task_id}: {exc}")
            final_status = "error"
        finally:
            await update_task_status(task_id, final_status)

    try:
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
    except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
        logging.warning(f"Error connecting to filman_server for notifications: {exc}")
        return

    logging.info(task)

    if task["task_type"] == "send_discord_notification":
        parts = task["task_job"].split(",")
        if len(parts) != 3:
            logging.error(f"Malformed notification task_job: {task['task_job']}")
            await update_task_status(task["task_id"], "error")
            return

        filmweb_id, media_type, media_id = parts
        await send_discord_notification_watched(
            bot,
            task["task_id"],
            filmweb_id,
            media_type,
            media_id,
        )


bot.load_extensions_from("./endpoints/")

if __name__ == "__main__":
    bot.run()
