from datetime import datetime

import hikari
import lightbulb

import csv
import io
import re

tools_plugin = lightbulb.Plugin("Tools")


@tools_plugin.command()
@lightbulb.command("tools", "Narzędzia bota")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def tools_group(_: lightbulb.SlashContext) -> None:
    pass


@tools_group.child
@lightbulb.option("channel", "kanał tekstowy", type=hikari.TextableChannel, required=True)
@lightbulb.option("ignore_bot", "ignorować wiadomości od botów", type=bool, required=False, default=True)
@lightbulb.command("extract_links_advanced", "Ekstrahuje linki filmweb/imdb/letterboxd z ostatnich 1000 wiadomości na kanale. Zwraca tytuły z Filmwebu.")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def extract_links_advanced_subcommand(ctx: lightbulb.SlashContext) -> None:

    async def create_filmweb_scrap_task(filmweb_id: str, is_movie: bool):
        async with ctx.bot.d.client_session.get(
            "http://filman_server:8000/tasks/create",
            json={
                "task_status": "queued",
                "task_type": "scrap_filmweb_movie" if is_movie else "scrap_filmweb_series",
                "task_job": filmweb_id
            }
        ) as resp:
            pass

    channel_id = ctx.options.channel.id
    ignore_bot = ctx.options.ignore_bot

    await ctx.respond(f"Rozpoczynam ekstrakcję linków z kanału <#{channel_id}>...\nTo może chwilę potrwać...")

    class link_info:
        def __init__(self, link: str, title: str, year: str, author: str):
            self.link = link
            self.title = title
            self.year = year
            self.author = author

    links: list[link_info] = []

    iterator = ctx.bot.rest.fetch_messages(channel_id).limit(1000)
    async for message in iterator:
        if ignore_bot and message.author.is_bot:
            continue

        content = message.content or ""

        if "filmweb.pl" in content:
            for part in content.split():
                if "filmweb.pl" in part:
                    links.append(link_info(link=part, title="", year="", author=str(message.author)))

        if "imdb.com" in content:
            for part in content.split():
                if "imdb.com" in part:
                    links.append(link_info(link=part, title="", year="", author=str(message.author)))

        if "letterboxd.com" in content:
            for part in content.split():
                if "letterboxd.com" in part:
                    links.append(link_info(link=part, title="", year="", author=str(message.author)))

    filmweb_with_data_hits = 0

    csv_buffer = io.StringIO()
    csv_writer = csv.writer(csv_buffer, delimiter=";")
    csv_writer.writerow(["platforma", "link", "tytuł", "rok", "autor wiadomości"])

    for link_entry in links:
        platform = ""
        if "filmweb.pl" in link_entry.link:
            platform = "filmweb"

            if match := re.search(r'/film/[^/]+-(\d+)', link_entry.link):
                filmweb_id = match.group(1)

                async with ctx.bot.d.client_session.get(
                    f"http://filman_server:8000/filmweb/movie/get?filmweb_id={filmweb_id}"
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        link_entry.title = data.get("title", "")
                        link_entry.year = data.get("year", "")

                        filmweb_with_data_hits += 1
                    else:
                        await create_filmweb_scrap_task(filmweb_id, is_movie=True)

            elif match := re.search(r'/serial/[^/]+-(\d+)', link_entry.link):
                filmweb_id = match.group(1)

                async with ctx.bot.d.client_session.get(
                    f"http://filman_server:8000/filmweb/series/get?filmweb_id={filmweb_id}"
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        link_entry.title = data.get("title", "")
                        link_entry.year = data.get("year", "")

                        filmweb_with_data_hits += 1
                    else:
                        await create_filmweb_scrap_task(filmweb_id, is_movie=False)

        elif "imdb.com" in link_entry.link:
            platform = "imdb"
        elif "letterboxd.com" in link_entry.link:
            platform = "letterboxd"

        csv_writer.writerow([platform, link_entry.link, link_entry.title, link_entry.year, link_entry.author])

    csv_buffer.seek(0)
    csv_bytes = io.BytesIO(csv_buffer.getvalue().encode('utf-8'))
    embed = hikari.Embed(
        title="Ekstrakcja linków zakończona",
        description=f"Znaleziono linki z ostatnich 1000 wiadomości na kanale <#{channel_id}>.",
        colour=0xFFC200,
        timestamp=datetime.now().astimezone()
    )
    embed.add_field(
        name="Statystyki",
        value=f"**Filmweb (z danymi):** {filmweb_with_data_hits} linków\n"
              f"**Filmweb (do scrapowania):** {len([l for l in links if 'filmweb.pl' in l.link]) - filmweb_with_data_hits} linków\n"
              f"**IMDb:** {len([l for l in links if 'imdb.com' in l.link])} linków\n"
              f"**Letterboxd:** {len([l for l in links if 'letterboxd.com' in l.link])} linków",
        inline=False
    )
    
    if len([l for l in links if 'filmweb.pl' in l.link]) - filmweb_with_data_hits > 0:
        embed.add_field(
            name="Informacja",
            value="Niektóre linki do Filmwebu nie miały dostępnych danych i zostały dodane do kolejki scrapowania. Możesz spróbować ponownie później c:",
            inline=False
        )

    embed.set_footer(
        text=f"Requested by {ctx.author}",
        icon=ctx.author.display_avatar_url,
    )
    

    await ctx.edit_last_response(
        content=None,
        embed=embed,
        attachment=hikari.Bytes(csv_bytes, f"links_channel_{channel_id}_advanced.csv")
    )

@tools_group.child
# @lightbulb.cooldowns(1, 10, lightbulb.UserBucket) to do: dodac cooldown
@lightbulb.option("channel", "kanał tekstowy", type=hikari.TextableChannel, required=True)
@lightbulb.option("ignore_bot", "ignorować wiadomości od botów", type=bool, required=False, default=True)
@lightbulb.command("extract_links_basic", "Ekstrahuje linki filmweb/imdb/letterboxd z ostatnich 1000 wiadomości na kanale")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def extract_links_basic_subcommand(ctx: lightbulb.SlashContext) -> None:
    channel_id = ctx.options.channel.id
    ignore_bot = ctx.options.ignore_bot
    
    # channel = await ctx.bot.rest.fetch_channel(channel_id)
    
    await ctx.respond(f"Rozpoczynam ekstrakcję linków z kanału <#{channel_id}>...\nTo może chwilę potrwać...")

    links = {"filmweb": set(), "imdb": set(), "letterboxd": set()}
    
    iterator = ctx.bot.rest.fetch_messages(channel_id).limit(1000)
    async for message in iterator:
        if ignore_bot and message.author.is_bot:
            continue

        content = message.content or ""

        if "filmweb.pl" in content:
            links["filmweb"].update(part for part in content.split() if "filmweb.pl" in part)
        if "imdb.com" in content:
            links["imdb"].update(part for part in content.split() if "imdb.com" in part)
        if "letterboxd.com" in content:
            links["letterboxd"].update(part for part in content.split() if "letterboxd.com" in part)

    csv_buffer = io.StringIO()
    csv_writer = csv.writer(csv_buffer, delimiter=";")
    csv_writer.writerow(["platforma", "link"])
    
    for platform, link_set in links.items():
        for link in sorted(link_set):
            csv_writer.writerow([platform, link])
    
    csv_buffer.seek(0)
    csv_bytes = io.BytesIO(csv_buffer.getvalue().encode('utf-8'))
    
    embed = hikari.Embed(
        title="Ekstrakcja linków zakończona",
        description=f"Znaleziono linki z ostatnich 1000 wiadomości na kanale <#{channel_id}>.",
        colour=0xFFC200,
        timestamp=datetime.now().astimezone()
    )
    
    embed.add_field(
        name="Statystyki",
        value=f"**Filmweb:** {len(links['filmweb'])} linków\n"
              f"**IMDb:** {len(links['imdb'])} linków\n"
              f"**Letterboxd:** {len(links['letterboxd'])} linków",
        inline=False
    )
    
    embed.set_footer(
        text=f"Requested by {ctx.author}",
        icon=ctx.author.display_avatar_url,
    )

    await ctx.edit_last_response(
        content=None,
        embed=embed,
        attachment=hikari.Bytes(csv_bytes, f"links_channel_{channel_id}.csv")
    )

    #
    # filmweb scrapping
    #
    
    for link in links["filmweb"]:
        movie_match = re.search(r'/film/[^/]+-(\d+)', link)
        series_match = re.search(r'/serial/[^/]+-(\d+)', link)
        
        if movie_match:
            movie_id = movie_match.group(1)
            async with ctx.bot.d.client_session.post(
                "http://filman_server:8000/tasks/create",
                json={
                    "task_status": "queued",
                    "task_type": "scrap_filmweb_movie",
                    "task_job": movie_id
                }
            ) as resp:
                pass
        
        elif series_match:
            series_id = series_match.group(1)
            async with ctx.bot.d.client_session.post(
                "http://filman_server:8000/tasks/create",
                json={
                    "task_status": "queued",
                    "task_type": "scrap_filmweb_series",
                    "task_job": series_id
                }
            ) as resp:
                pass



def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(tools_plugin)
