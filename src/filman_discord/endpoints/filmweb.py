import logging
from datetime import datetime

import hikari
import lightbulb

from filman_discord.utils.filmweb_w2s_logic import MediaType, process_media

tracker_plugin = lightbulb.Plugin("Filmweb")


@tracker_plugin.command
@lightbulb.command("filmweb", "interakcje z filmwebem")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def tracker_group(_: lightbulb.SlashContext) -> None:
    pass


@tracker_group.child
# @lightbulb.cooldown(1, 60, bucket=lightbulb.CooldownBucketType.user)
@lightbulb.option("filmweb_username", "nazwa użytkownika na filmwebie", required=True, type=str)
@lightbulb.command("me", "monitoruj swoje konto filmweb", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def me_subcommand(ctx: lightbulb.SlashContext, filmweb_username: str) -> None:
    async with ctx.bot.d.client_session.post(
        "http://filman_server:8000/users/create",
        json={"discord_id": ctx.author.id},
    ) as resp1:
        pass

    async with ctx.bot.d.client_session.get(
        "http://filman_server:8000/users/get",
        params={"discord_id": ctx.author.id},
    ) as resp2:
        if not resp2.ok:
            await ctx.respond(
                f"API zwróciło {resp2.status} status :c (2)",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return
        else:
            resp2_json = await resp2.json()
            user_id = resp2_json.get("id")

    async with ctx.bot.d.client_session.post(
        "http://filman_server:8000/filmweb/user/mapping/set",
        json={"user_id": user_id, "filmweb_id": filmweb_username},
    ) as resp3:
        if not resp3.ok:
            if resp3.status == 404:
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
            elif resp3.status == 409:
                embed = hikari.Embed(
                    title=f"Użytkownik '{filmweb_username}' jest już monitorowany!",
                    colour=0xFF4400,
                    timestamp=datetime.now().astimezone(),
                )
                embed.add_field(
                    name="Zmiana konta filmweb",
                    value="""Jeśli chcesz zmienić monitorowane konto filmweb, musisz najpierw usunąć obecne!
                    W tym celu użyj komendy `/filmweb cancel`""",
                    inline=True,
                )
                embed.set_footer(
                    text=f"Requested by {ctx.author}",
                    icon=ctx.author.display_avatar_url,
                )
                await ctx.respond(embed, flags=hikari.MessageFlag.EPHEMERAL)
            else:
                await ctx.respond(
                    f"API zwróciło {resp3.status} status :c",
                    flags=hikari.MessageFlag.EPHEMERAL,
                )
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
        value="Aby włączyć powiadomienia na tym serwerze, użyj komendy `/filmweb here`",
        inline=True,
    )
    embed.set_footer(
        text=f"Requested by {ctx.author}",
        icon=ctx.author.display_avatar_url,
    )
    await ctx.respond(embed)

    # scrap user watched data
    async with ctx.bot.d.client_session.get(f"http://filman_server:8000/tasks/new/scrap/filmweb/users/movies") as resp:
        pass

    async with ctx.bot.d.client_session.get(f"http://filman_server:8000/tasks/new/scrap/filmweb/users/series") as resp:
        pass

    return


@tracker_group.child
@lightbulb.command("here", "powiadamiaj na tym serwerze", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def here_subcommand(ctx: lightbulb.SlashContext) -> None:

    async with ctx.bot.d.client_session.get(
        f"http://filman_server:8000/users/add_to_guild?discord_id={ctx.author.id}&discord_guild_id={ctx.guild_id}"
    ) as resp:
        if not resp.ok:
            if resp.status == 404:
                embed = hikari.Embed(
                    title=f"Twoje konto nie jest monitorowane! Użyj `/filmweb me`",
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
                    title=f"Nie znaleziono serwera w bazie danych! Użyj `/configure channel`, aby go dodać!",
                    colour=0xFF4400,
                    timestamp=datetime.now().astimezone(),
                )

                embed.set_footer(
                    text=f"Requested by {ctx.author}",
                    icon=ctx.author.display_avatar_url,
                )

                await ctx.respond(embed)
                return

            if resp.status == 409:
                embed = hikari.Embed(
                    title=f"Już monitorujesz ten serwer!",
                    colour=0xFF4400,
                    timestamp=datetime.now().astimezone(),
                )

                embed.set_footer(
                    text=f"Requested by {ctx.author}",
                    icon=ctx.author.display_avatar_url,
                )

                await ctx.respond(embed, flags=hikari.MessageFlag.EPHEMERAL)
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
    async with ctx.bot.d.client_session.delete(
        f"http://filman_server:8000/users/remove_from_guild?discord_user_id={ctx.author.id}&discord_guild_id={ctx.guild_id}"
    ) as resp:
        if not resp.ok:
            if resp.status == 404:
                embed = hikari.Embed(
                    title=f"Nie monitorujesz tego serwera!",
                    colour=0xFF4400,
                    timestamp=datetime.now().astimezone(),
                )

                embed.set_footer(
                    text=f"Requested by {ctx.author}",
                    icon=ctx.author.display_avatar_url,
                )

                await ctx.respond(embed, flags=hikari.MessageFlag.EPHEMERAL)
                return

            await ctx.respond(
                f"API zwróciło {resp.status} status :c",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        embed = hikari.Embed(
            title=f"Przestałeś monitorować ten serwer!",
            colour=0xFFC200,
            timestamp=datetime.now().astimezone(),
        )

        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon=ctx.author.display_avatar_url,
        )

        await ctx.respond(embed)


@tracker_group.child
@lightbulb.command("stop_everything", "przestań powiadamiać na WSZYSTKICH serwerach", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def stop_everything_subcommand(ctx: lightbulb.SlashContext) -> None:
    async with ctx.bot.d.client_session.delete(
        f"http://filman_server:8000/users/remove_from_all_guilds?discord_user_id={ctx.author.id}"
    ) as resp:
        if not resp.ok:
            if resp.status == 404:
                embed = hikari.Embed(
                    title=f"Nie monitorujesz żadnego serwera!",
                    colour=0xFF4400,
                    timestamp=datetime.now().astimezone(),
                )

                embed.set_footer(
                    text=f"Requested by {ctx.author}",
                    icon=ctx.author.display_avatar_url,
                )

                await ctx.respond(embed, flags=hikari.MessageFlag.EPHEMERAL)
                return

            await ctx.respond(
                f"API zwróciło {resp.status} status :c",
                flags=hikari.MessageFlag.EPHEMERAL,
            )
            return

        embed = hikari.Embed(
            title=f"Przestałeś monitorować WSZYSTKIE serwery!",
            colour=0xFFC200,
            timestamp=datetime.now().astimezone(),
        )

        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon=ctx.author.display_avatar_url,
        )

        await ctx.respond(embed)


# @tracker_group.child
# @lightbulb.command("list", "lista powiadomień", pass_options=True)


@tracker_group.child
@lightbulb.command("cancel", "przestań monitorować konto filmweb", pass_options=True)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def cancel_subcommand(ctx: lightbulb.SlashContext) -> None:
    async with ctx.bot.d.client_session.delete(
        "http://filman_server:8000/filmweb/user/mapping/delete",
        params={"discord_id": ctx.author.id},
    ) as resp:
        if resp.status == 404:
            embed = hikari.Embed(
                title=f"Nie monitorujesz żadnego konta filmweb!",
                colour=0xFF4400,
                timestamp=datetime.now().astimezone(),
            )
            embed.set_footer(
                text=f"Requested by {ctx.author}",
                icon=ctx.author.display_avatar_url,
            )
            await ctx.respond(embed, flags=hikari.MessageFlag.EPHEMERAL)
            return

        if not resp.ok:
            embed = hikari.Embed(
                title=f"API zwróciło {resp.status} status :c",
                colour=0xFF4400,
                timestamp=datetime.now().astimezone(),
            )
            embed.set_footer(
                text=f"Requested by {ctx.author}",
                icon=ctx.author.display_avatar_url,
            )
            await ctx.respond(embed, flags=hikari.MessageFlag.EPHEMERAL)
            return

        embed = hikari.Embed(
            title=f"To koniec monitorowania twojego konta filmweb!",
            colour=0xFFC200,
            timestamp=datetime.now().astimezone(),
        )

        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon=ctx.author.display_avatar_url,
        )

        await ctx.respond(embed, flags=hikari.MessageFlag.EPHEMERAL)
        return


# todo: draw within common friends list
@tracker_group.child
@lightbulb.option("user5", "Piąty użytkownik", type=hikari.User, required=False)
@lightbulb.option("user4", "Czwarty użytkownik", type=hikari.User, required=False)
@lightbulb.option("user3", "Trzeci użytkownik", type=hikari.User, required=False)
@lightbulb.option("user2", "Drugi użytkownik", type=hikari.User, required=False)
@lightbulb.option("user1", "Pierwszy użytkownik (wymagany)", type=hikari.User, required=True)
@lightbulb.option(
    "common",
    "Losuj tylko z wspólnych elemntów list",
    type=bool,
    required=False,
    autocomplete=False,
)
@lightbulb.option(
    "typ",
    "Wybierz co chcesz losować: film / serial",
    type=str,
    required=True,
    choices=["film", "serial"],
    default="film",
)
@lightbulb.command(
    "w2s",
    "Wylosuj film lub serial z listy 'chcę obejrzeć' dla użytkownika/użytkowników",
    pass_options=True,
)
@lightbulb.implements(lightbulb.SlashSubCommand)
async def w2s_subcommand(
    ctx: lightbulb.SlashContext,
    typ: str,
    user1: hikari.User,
    user2: hikari.User = None,
    user3: hikari.User = None,
    user4: hikari.User = None,
    user5: hikari.User = None,
    common: bool = False,
) -> None:
    users = [user1, user2, user3, user4, user5]
    mentioned_users = [user.mention for user in users if user is not None]

    for user in users:
        if user is not None:
            if user.is_bot:
                embed = hikari.Embed(
                    title="Nie możesz losować filmów dla bota, zostaw go w spokoju!",
                    colour=0xFF4400,
                    timestamp=datetime.now().astimezone(),
                )
                embed.set_footer(
                    text=f"Requested by {ctx.author}",
                    icon=ctx.author.display_avatar_url,
                )
                return await ctx.respond(embed)

    if len(mentioned_users) == 0:
        embed = hikari.Embed(
            title="Nie podano użytkowników!",
            colour=0xFF4400,
            timestamp=datetime.now().astimezone(),
        )
        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon=ctx.author.display_avatar_url,
        )
        return await ctx.respond(embed)

    if len(mentioned_users) == 1 and common is True:
        embed = hikari.Embed(
            title="Nie możesz losować wspólnych filmów dla jednej osoby, przecież to nie ma sensu xd",
            colour=0xFF4400,
            timestamp=datetime.now().astimezone(),
        )
        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon=ctx.author.display_avatar_url,
        )
        return await ctx.respond(embed)

    response = f"Oznaczono {len(mentioned_users)} użytkowników:\n" + "\n".join(mentioned_users)

    embed = hikari.Embed(
        title=f"Losowanie `{typ}`...",
        description=response,
        colour=0xFFC200,
        timestamp=datetime.now().astimezone(),
    )

    await ctx.respond(embed)

    logging.debug(f"Processing users: {users}")

    media_type = MediaType.FILM if typ == "film" else MediaType.SERIAL

    await ctx.edit_last_response(content=await process_media(users, common, media_type=media_type), embed=None)


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(tracker_plugin)
