from datetime import datetime

import hikari
import lightbulb

configure_plugin = lightbulb.Plugin("Configure")


@configure_plugin.command
@lightbulb.command("configure", "Konfiguracja bota")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def configure_group(_: lightbulb.SlashContext) -> None:
    pass


def permissions_for(member: hikari.Member) -> hikari.Permissions:
    """
    Get the guild permissions for the given member.

    Args:
        member (:obj:`hikari.Member`): Member to get permissions for.

    Returns:
        :obj:`hikari.Permissions`: Member's guild permissions.

    Warning:
        This method relies on the cache to work. If the cache is not available then :obj:`hikari.Permissions.NONE`
        will be returned.
    """
    permissions = hikari.Permissions.NONE
    for role in member.get_roles():
        permissions |= role.permissions

    guild = member.get_guild()

    if hikari.Permissions.ADMINISTRATOR in permissions or guild and member.id == guild.owner_id:
        return hikari.Permissions.all_permissions()

    return permissions


@configure_group.child
@lightbulb.option("text_channel", "kanał tekstowy", type=hikari.TextableChannel, required=True)
@lightbulb.command("channel", "ustaw kanał z powiadomieniami", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def channel_subcommand(ctx: lightbulb.SlashContext, text_channel: hikari.TextableChannel) -> None:
    author_permissions = permissions_for(ctx.member)

    if hikari.Permissions.ADMINISTRATOR not in author_permissions:
        embed = hikari.Embed(
            title="Tylko administratorzy serwera mogą to zrobić!",
            colour=0xFF4400,
            timestamp=datetime.now().astimezone(),
        )

        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon=ctx.author.display_avatar_url,
        )

        await ctx.respond(embed, flags=hikari.MessageFlag.EPHEMERAL)
        return

    async with ctx.bot.d.client_session.post(
        "http://filman_server:8000/discord/configure/guild",
        json={"discord_guild_id": ctx.guild_id, "discord_channel_id": text_channel.id},
    ) as resp:
        if not resp.ok:
            await ctx.respond(
                f"Coś poszło nie tak! {resp.status} {resp.reason}",
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

    embed = hikari.Embed(
        title="Wystąpił błąd!",
        description=f"```{exception}```",
        colour=0xFF4400,
        timestamp=datetime.now().astimezone(),
    )

    embed.set_footer(
        text=f"Requested by {event.context.author}",
        icon=event.context.author.display_avatar_url,
    )

    await event.context.respond(embed, flags=hikari.MessageFlag.EPHEMERAL)


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(configure_plugin)
