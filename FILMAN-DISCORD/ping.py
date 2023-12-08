from datetime import datetime
from typing import Optional

import hikari
import lightbulb

user_plugin = lightbulb.Plugin("User")


@info_plugin.command
@lightbulb.app_command_permissions(dm_enabled=False)
@lightbulb.option(
    "user", "The user to get information about.", hikari.User, required=False
)
@lightbulb.command("userinfo", "Get info on a server member.", pass_options=True)
@lightbulb.implements(lightbulb.SlashCommand)
async def userinfo(
    ctx: lightbulb.SlashContext, user: Optional[hikari.User] = None
) -> None:
    assert ctx.guild_id is not None

    user = user or ctx.author

    user = ctx.bot.cache.get_member(ctx.guild_id, user)

    if not user:
        await ctx.respond("That user is not in this server.")

        return

    created_at = int(user.created_at.timestamp())

    joined_at = int(user.joined_at.timestamp())

    roles = [f"<@&{role}>" for role in user.role_ids if role != ctx.guild_id]

    embed = (
        hikari.Embed(
            title=f"User Info - {user.display_name}",
            description=f"ID: `{user.id}`",
            colour=0x3B9DFF,
            timestamp=datetime.now().astimezone(),
        )
        .set_footer(
            text=f"Requested by {ctx.author}",
            icon=ctx.author.display_avatar_url,
        )
        .set_thumbnail(user.avatar_url)
        .add_field(
            "Bot?",
            "Yes" if user.is_bot else "No",
            inline=True,
        )
        .add_field(
            "Created account on",
            f"<t:{created_at}:d>\n(<t:{created_at}:R>)",
            inline=True,
        )
        .add_field(
            "Joined server on",
            f"<t:{joined_at}:d>\n(<t:{joined_at}:R>)",
            inline=True,
        )
        .add_field(
            "Roles",
            ", ".join(roles) if roles else "No roles",
            inline=False,
        )
    )

    await ctx.respond(embed)


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(user_plugin)
