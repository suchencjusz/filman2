from datetime import datetime

import hikari
import lightbulb

help_plugin = lightbulb.Plugin("Help")


@help_plugin.command
@lightbulb.command("help", "pomoc")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def help_group(_: lightbulb.SlashContext) -> None:
    pass


@help_group.child
@lightbulb.command("tracker", "powiadomienia i śledzenie użytkownika")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def tracker_subcommand(ctx: lightbulb.SlashContext) -> None:
    embed = hikari.Embed(title="`/tracker`", colour=0xFFC200, timestamp=datetime.now().astimezone())

    embed.add_field(name="`/tracker me`", value="Monitoruje konto filmweb")

    embed.add_field(
        name="`/tracker cancel`",
        value="Anuluje monitorowanie konta filmweb i usuwa dane z bazy danych",
    )

    embed.add_field(
        name="`/tracker stop`", value="Anuluje wysyłanie powiadomień na danym serwerze"
    )

    embed.add_field(
        name="`/tracker here`",
        value="Dopisuje użytkownika do listy powiadomień na danym serwerze",
    )

    embed.set_footer(
        text=f"Requested by {ctx.author}",
        icon=ctx.author.display_avatar_url,
    )

    await ctx.respond(embed)


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(help_plugin)
