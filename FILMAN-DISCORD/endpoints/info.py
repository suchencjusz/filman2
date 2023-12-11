from datetime import datetime

import hikari
import lightbulb

info_plugin = lightbulb.Plugin("Info")


@info_plugin.command
@lightbulb.command("info", "informacje o bocie")
@lightbulb.implements(lightbulb.SlashCommand)
async def info_command(ctx: lightbulb.SlashContext) -> None:
    embed = hikari.Embed(
        title="`Filman`", colour=0xFFC200, timestamp=datetime.now().astimezone()
    )

    embed.add_field(
        name="Wersja i ostatnia aktualizacja",
        value="`1.0.0` - `2023-12-11`",
    )

    embed.add_field(
        name="Autor",
        value="`@suchencjusz`",
    )

    embed.set_footer(
        text=f"Requested by {ctx.author}",
        icon=ctx.author.display_avatar_url,
    )

    await ctx.respond(embed)


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(info_plugin)