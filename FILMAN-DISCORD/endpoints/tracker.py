from datetime import datetime
from typing import Optional

import hikari
import lightbulb

tracker_plugin = lightbulb.Plugin("Tracker")


@tracker_plugin.command
@lightbulb.command("tracker", "Zarządzaj powiadomieniami na serwerze")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def tracker_group(_: lightbulb.SlashContext) -> None:
    pass


@tracker_group.child
# @lightbulb.cooldown(1, 60, bucket=lightbulb.CooldownBucketType.user)
@lightbulb.option(
    "filmweb_username", "nazwa użytkownika na filmwebie", required=True, type=str
)
@lightbulb.command("me", "monitoruj swoje konto filmweb", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def me_subcommand(ctx: lightbulb.SlashContext, filmweb_username: str) -> None:
    async with ctx.bot.d.client_session.post(
        "http://filman-server:8000/user/create",
        json={"id_discord": ctx.author.id, "id_filmweb": filmweb_username},
    ) as resp:
        if not resp.ok:
            if resp.status == 404:
                embed = hikari.Embed(
                    title=f"Nie znaleziono użytkownika '{filmweb_username}' na filmwebie!",
                    colour=0xFF4400,
                    timestamp=datetime.now().astimezone(),
                )

                embed.set_footer(
                    text=f"Requested by {ctx.author}",
                    icon=ctx.author.display_avatar_url,
                )

                await ctx.respond(embed, flags=hikari.MessageFlag.EPHEMERAL)

            if resp.status == 409:
                embed = hikari.Embed(
                    title=f"Użytkownik '{filmweb_username}' jest już monitorowany!",
                    colour=0xFF4400,
                    timestamp=datetime.now().astimezone(),
                )

                embed.add_field(
                    name="Zmiana konta filmweb",
                    value="""Jeśli chcesz zmienić monitorowane konto filmweb, musisz najpierw usunąć obecne!
                    W tym celu użyj komendy `/tracker cancel`""",
                    inline=True,
                )

                embed.set_footer(
                    text=f"Requested by {ctx.author}",
                    icon=ctx.author.display_avatar_url,
                )

                await ctx.respond(embed, flags=hikari.MessageFlag.EPHEMERAL)

            return

        embed = hikari.Embed(
            title=f"Konto {filmweb_username} zostało dodane!",
            colour=0xFFC200,
            timestamp=datetime.now().astimezone(),
        )

        embed.add_field(
            name="Inicializacja",
            value="Inicjalizacja twoich danych może chwilę potrwać, więc nie martw się, jeśli nie dostaniesz od razu powiadomienia!",
            inline=True,
        )

        embed.add_field(
            name="Powiadomienia na tym serwerze",
            value="Aby włączyć powiadomienia na tym serwerze, użyj komendy `/tracker here`",
            inline=True,
        )

        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon=ctx.author.display_avatar_url,
        )

        await ctx.respond(embed)


@tracker_group.child
@lightbulb.command("here", "powiadamiaj na tym serwerze", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def here_subcommand(ctx: lightbulb.SlashContext) -> None:
    async with ctx.bot.d.client_session.post(
        "http://filman-server:8000/discord/user/add",
        json={"id_discord": ctx.author.id, "id_guild": ctx.guild_id},
    ) as resp:
        if not resp.ok:
            if resp.status == 404:
                embed = hikari.Embed(
                    title=f"Nie znaleziono Ciebie w bazie danych :c Użyj /tracker me, aby się dodać!",
                    colour=0xFF4400,
                    timestamp=datetime.now().astimezone(),
                )

                embed.set_footer(
                    text=f"Requested by {ctx.author}",
                    icon=ctx.author.display_avatar_url,
                )

                await ctx.respond(embed, flags=hikari.MessageFlag.EPHEMERAL)
                return

            if resp.status == 405:
                embed = hikari.Embed(
                    title=f"Nie znaleziono serwera w bazie danych :c Użyj /configure channel, aby go dodać!",
                    colour=0xFF4400,
                    timestamp=datetime.now().astimezone(),
                )

                embed.set_footer(
                    text=f"Requested by {ctx.author}",
                    icon=ctx.author.display_avatar_url,
                )

                await ctx.respond(embed)
                return

            await ctx.respond(
                f"API zwróciło {resp.status} status :c",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        embed = hikari.Embed(
            title=f"Powiadomienia zostały skonfigurowane!",
            colour=0xFFC200,
            timestamp=datetime.now().astimezone(),
        )

        embed.add_field(
            name="Użytkownik",
            value=ctx.author.mention,
            inline=True,
        )

        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon=ctx.author.display_avatar_url,
        )

        await ctx.respond(embed)


@tracker_group.child
@lightbulb.command("stop", "przestań powiadamiać na tym serwerze", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def stop_subcommand(ctx: lightbulb.SlashContext) -> None:
    async with ctx.bot.d.client_session.post(
        "http://filman-server:8000/discord/user/stop",
        json={"id_discord": ctx.author.id, "guild_id": ctx.guild_id},
    ) as resp:
        if not resp.ok:
            await ctx.respond(
                f"API zwróciło {resp.status} status :c",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        embed = hikari.Embed(
            title=f"Powiadomienia dla `{ctx.author}` zostały wyłączone!",
            colour=0xFFC200,
            timestamp=datetime.now().astimezone(),
        )

        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon=ctx.author.display_avatar_url,
        )

        await ctx.respond(embed)


@tracker_group.child
@lightbulb.command(
    "cancel", "przestań powiadamiać na WSZYSTKICH serwerach", pass_options=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def cancel_subcommand(ctx: lightbulb.SlashContext) -> None:
    async with ctx.bot.d.client_session.post(
        "http://filman-server:8000/discord/user/cancel",
        json={"id_discord": ctx.author.id},
    ) as resp:
        if not resp.ok:
            await ctx.respond(
                f"API zwróciło {resp.status} status :c",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        embed = hikari.Embed(
            title=f"Powiadomienia na WSZYSTKICH serwerach zostały wyłączone!",
            colour=0xFFC200,
            timestamp=datetime.now().astimezone(),
        )

        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon=ctx.author.display_avatar_url,
        )

        await ctx.respond(embed)


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(tracker_plugin)


# @tracker_group.child
# @lightbulb.command("list", "lista powiadomień", pass_options=True)
