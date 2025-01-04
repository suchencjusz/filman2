from datetime import datetime

import hikari
import lightbulb

info_plugin = lightbulb.Plugin("Info")


@info_plugin.command()
@lightbulb.command("info", "informacje o bocie")
@lightbulb.implements(lightbulb.SlashCommand)
async def info_group(ctx: lightbulb.SlashContext) -> None:
    pass


@info_group.child
@lightbulb.command("basic", "podstawowe informacje o bocie")
@lightbulb.implements(lightbulb.SlashCommand)
async def info_basic_command(ctx: lightbulb.SlashContext) -> None:
    embed = hikari.Embed(title="`Filman`", colour=0xFFC200, timestamp=datetime.now().astimezone())

    embed.add_field(
        name="Wersja i ostatnia aktualizacja",
        value="`1.1.8v` - `2025-01-04`",
    )

    embed.add_field(
        name="Autor",
        value="`@suchencjusz`",
    )

    embed.add_field(
        name="Repozytorium",
        value="https://github.com/suchencjusz/filman2",
    )

    embed.set_footer(
        text=f"Requested by {ctx.author}",
        icon=ctx.author.display_avatar_url,
    )

    await ctx.respond(embed)


@info_group.child
@lightbulb.command("database", "informacje o bazie danych")
@lightbulb.implements(lightbulb.SlashCommand)
async def info_database_command(ctx: lightbulb.SlashContext) -> None:
    async with ctx.bot.d.client_session.get("http://filman_server:8000/utils/database_info") as response:
        data = await response.json()

    embed = hikari.Embed(title="`Filman`", colour=0xFFC200, timestamp=datetime.now().astimezone())

    embed.add_field(
        name=f"W bazie danych znajduje się {data['users_count']} użytkowników \n którzy wszyscy obejrzeli {data['filmweb_watched_movies']} filmów \n oraz {data['filmweb_watched_series']} seriali, \n a także jest zarejestrowanych {data['discord_guilds']} serwerów.",
        value="",
    )

    embed.set_footer(
        text=f"Requested by {ctx.author}",
        icon=ctx.author.display_avatar_url,
    )

    await ctx.respond(embed)


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(info_plugin)
