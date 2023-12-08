from datetime import datetime
from typing import Optional, Required

import hikari
import asyncio
import lightbulb

configure_plugin = lightbulb.Plugin("Configure")


@configure_plugin.command
@lightbulb.command("configure", "Configure the bot.")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def configure_group(_: lightbulb.SlashContext) -> None:
    pass


@configure_group.child
@lightbulb.option(
    "text_channel", "text channel", type=hikari.TextableChannel, required=True
)
@lightbulb.command(
    "channel", "set the channel for the bot to post in", pass_options=True
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def channel_subcommand(
    ctx: lightbulb.SlashContext, text_channel: hikari.TextableChannel
) -> None:
    async with ctx.bot.d.client_session.get(
        f"http://localhost:8000/discord/configure/guild?guild_id={ctx.guild_id}&channel_id={text_channel.id}"
    ) as resp:
        if not resp.ok:
            await ctx.respond(
                f"API returned a {resp.status} status :c",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        embed = hikari.Embed(
            title=f"Kanał z powiadomieniami został skonfigurowany! <#{text_channel.id}>",
            colour=0xFFC200,
            timestamp=datetime.now().astimezone(),
        )

        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon=ctx.author.display_avatar_url,
        )

        await ctx.respond(embed)


@configure_group.set_error_handler
async def configure_group_error_handler(event: lightbulb.CommandErrorEvent) -> None:
    exception = event.exception.__cause__ or event.exception

    if isinstance(exception, lightbulb.errors.MissingRequiredOption):
        embed = hikari.Embed(
            title="Missing required option!",
            description=f"Option `{exception.option_name}` is required!",
            colour=0xFF4400,
            timestamp=datetime.now().astimezone(),
        )

        embed.set_footer(
            text=f"Requested by {event.context.author}",
            icon=event.context.author.display_avatar_url,
        )

        await event.context.respond(embed)

    elif isinstance(exception, lightbulb.errors.BadArgument):
        embed = hikari.Embed(
            title="Bad argument!",
            description=f"Option `{exception.option_name}` is invalid!",
            colour=0xFF4400,
            timestamp=datetime.now().astimezone(),
        )

        embed.set_footer(
            text=f"Requested by {event.context.author}",
            icon=event.context.author.display_avatar_url,
        )

        await event.context.respond(embed)

    elif isinstance(exception, lightbulb.errors.MissingRequiredSubCommand):
        embed = hikari.Embed(
            title="Missing required subcommand!",
            description=f"Subcommand `{exception.subcommand_name}` is required!",
            colour=0xFF4400,
            timestamp=datetime.now().astimezone(),
        )

        embed.set_footer(
            text=f"Requested by {event.context.author}",
            icon=event.context.author.display_avatar_url,
        )

        await event.context.respond(embed)

    await event.context.respond(
        "Something went wrong :c", flags=hikari.MessageFlag.EPHEMERAL
    )


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(configure_plugin)
