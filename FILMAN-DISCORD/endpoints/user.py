from datetime import datetime
from typing import Optional, Required

import hikari
import lightbulb

user_plugin = lightbulb.Plugin("User")


@user_plugin.command
@lightbulb.command("user", "Get info on a server member.")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def user_group(_: lightbulb.SlashContext) -> None:
    pass


@user_group.child
@lightbulb.option("filmweb_id", "filmweb username", type=str, required=True)
@lightbulb.option("discord_id", "discord user id", type=str, required=True)
@lightbulb.command("add", "add somebody to the database", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def add_subcommand(
    ctx: lightbulb.SlashContext, filmweb_id: str, discord_id: str
) -> None:
    discord_id = int(discord_id)

    # await ctx.respond(f"Added {filmweb_id} {discord_id} to the database")

    async with ctx.bot.d.client_session.get(
        f"http://localhost:8000/user/create?id_filmweb={filmweb_id}&id_discord={discord_id}"
    ) as resp:
        if not resp.ok:
            await ctx.respond(
                f"API returned a {resp.status} status :c",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        data = await resp.json()
        await ctx.respond(f"Added {filmweb_id} {discord_id} to the database")


@user_group.child
@lightbulb.option("filmweb_id", "filmweb username", type=str, required=True)
@lightbulb.command("delete", "delete somebody from the database", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def delete_subcommand(ctx: lightbulb.SlashContext, filmweb_id: str) -> None:
    async with ctx.bot.d.client_session.get(
        f"http://localhost:8000/user/delete?id_filmweb={filmweb_id}"
    ) as resp:
        if not resp.ok:
            await ctx.respond(
                f"API returned a {resp.status} status :c",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        data = await resp.json()
        await ctx.respond(f"Deleted {filmweb_id} from the database")


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(user_plugin)
