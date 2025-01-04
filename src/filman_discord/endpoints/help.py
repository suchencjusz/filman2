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
@lightbulb.command("configure", "konfiguracja serwera")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def configure_subcommand(ctx: lightbulb.SlashContext) -> None:
    embed = hikari.Embed(title="`/configure`", colour=0xFFC200, timestamp=datetime.now().astimezone())

    embed.add_field(name="`/configure channel`", value="Ustawia kanał powiadomień")

    embed.set_footer(
        text=f"Requested by {ctx.author}",
        icon=ctx.author.display_avatar_url,
    )

    await ctx.respond(embed)


@help_group.child
@lightbulb.command("filmweb", "akcje związane z kontem filmweb")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def filmweb_subcommand(ctx: lightbulb.SlashContext) -> None:
    embed = hikari.Embed(title="`/filmweb`", colour=0xFFC200, timestamp=datetime.now().astimezone())

    embed.add_field(
        name="`/filmweb me`",
        value="Monitoruje konto filmweb",
    )

    embed.add_field(
        name="`/filmweb cancel`",
        value="Anuluje monitorowanie konta filmweb i usuwa dane z bazy danych",
    )

    embed.add_field(
        name="`/filmweb stop`",
        value="Anuluje wysyłanie powiadomień na danym serwerze",
    )

    embed.add_field(
        name="`/filmweb stop_everything`",
        value="Anuluje wysyłanie powiadomień na wszystkich serwerach - usuwa dane użytkownika z bazy danych",
    )

    embed.add_field(
        name="`/filmweb here`",
        value="Dopisuje użytkownika do listy powiadomień na danym serwerze",
    )

    embed.add_field(
        name="`/filmweb w2s`",
        value="Losuje film/serial z list/y użytkowników \n opcja common losuje film z wspólnych elementów wszystkich użytkowników",
    )

    embed.set_footer(
        text=f"Requested by {ctx.author}",
        icon=ctx.author.display_avatar_url,
    )

    await ctx.respond(embed)


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(help_plugin)
