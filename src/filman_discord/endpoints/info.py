from datetime import datetime

import hikari
import lightbulb

info_plugin = lightbulb.Plugin("Info")


@info_plugin.command()
@lightbulb.command("info", "informacje o bocie")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def info_group(_: lightbulb.SlashContext) -> None:
    pass


@info_group.child
@lightbulb.command("basic", "podstawowe informacje o bocie")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def info_basic_command(ctx: lightbulb.SlashContext) -> None:
    embed = hikari.Embed(title="`Filman`", colour=0xFFC200, timestamp=datetime.now().astimezone())

    embed.add_field(
        name="Wersja i ostatnia aktualizacja",
        value="`1.1.9v` - `2025-10-19`",
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
@lightbulb.implements(lightbulb.SlashSubCommand)
async def info_database_command(ctx: lightbulb.SlashContext) -> None:
    async with ctx.bot.d.client_session.get("http://filman_server:8000/utils/database_info") as response:
        data = await response.json()

    embed = hikari.Embed(title="`Filman`", colour=0xFFC200, timestamp=datetime.now().astimezone())

    embed.add_field(
        name="Informacje o bazie danych",
        value=f"W bazie danych znajduje się {data['users_count']} użytkowników, wszyscy obejrzeli {data['filmweb_watched_movies']} filmów oraz {data['filmweb_watched_series']} seriali, a w bazie jest zarejestrowanych {data['discord_guilds']} serwerów.",
    )

    embed.set_footer(
        text=f"Requested by {ctx.author}",
        icon=ctx.author.display_avatar_url,
    )

    await ctx.respond(embed)


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(info_plugin)
