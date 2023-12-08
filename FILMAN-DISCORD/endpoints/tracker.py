from datetime import datetime
from typing import Optional, Required

import hikari
import lightbulb

tracker_plugin = lightbulb.Plugin("Tracker")


@tracker_plugin.command
@lightbulb.command("tracker", "Zarządzaj powiadomieniami na serwerze")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def tracker_group(_: lightbulb.SlashContext) -> None:
    pass


@tracker_group.child
@lightbulb.option(
    "filmweb_id", "twoja użytkownika na filmwebie", type=str, required=True
)
@lightbulb.command("me", "powiadamiaj na tym serwerze", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def me_subcommand(ctx: lightbulb.SlashContext, filmweb_id: str) -> None:
    async with ctx.bot.d.client_session.get(
        f"http://localhost:8000/discord/user/add?id_filmweb={filmweb_id}&id_guild={ctx.guild_id}"
    ) as resp:
        if not resp.ok:
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
            name="Filmweb ID",
            value=filmweb_id,
            inline=True,
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
    async with ctx.bot.d.client_session.get(
        f"/discord/user/stop?id_discord={ctx.author.id}&guild_id={ctx.guild_id}"
    ) as resp:
        if not resp.ok:
            await ctx.respond(
                f"API zwróciło {resp.status} status :c",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        embed = hikari.Embed(
            title=f"Powiadomienia zostały wyłączone!",
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
    async with ctx.bot.d.client_session.get(
        f"/discord/user/cancel?id_discord={ctx.author.id}"
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
