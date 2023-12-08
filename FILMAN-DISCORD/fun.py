import hikari
import asyncio
import lightbulb


fun_plugin = lightbulb.Plugin("Fun")


ANIMALS = {
    "Bird": "🐦",
    "Cat": "🐱",
    "Dog": "🐶",
    "Fox": "🦊",
    "Kangaroo": "🦘",
    "Koala": "🐨",
    "Panda": "🐼",
    "Raccoon": "🦝",
    "Red Panda": "🐼,"
}


@fun_plugin.command
@lightbulb.command("fun", "All the entertainment commands you'll ever need!")
@lightbulb.implements(lightbulb.SlashCommandGroup)
async def fun_group(_: lightbulb.SlashContext) -> None:
    pass  # as slash commands cannot have their top-level command run, we simply pass here


@fun_group.child
@lightbulb.command("animal", "Get a fact & picture of a cute animal :3")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def animal_subcommand(ctx: lightbulb.SlashContext) -> None:
    select_menu = (
        ctx.bot.rest.build_message_action_row()
        .add_select_menu(hikari.ComponentType.TEXT_SELECT_MENU, "animal_select")
    )

    for name, emoji in ANIMALS.items():
        select_menu.add_option(
            name,  # the label, which users see
            name.lower().replace(" ", "_"),  # the value, which is used by us later
        ).set_emoji(emoji).add_to_menu()

    resp = await ctx.respond(
        "Pick an animal from the dropdown :3",
        component=select_menu.add_to_container(),
    )

    msg = await resp.message()

    try:
        event = await ctx.bot.wait_for(
            hikari.InteractionCreateEvent,
            timeout=60,
            predicate=lambda e: isinstance(e.interaction, hikari.ComponentInteraction)
            and e.interaction.user.id == ctx.author.id
            and e.interaction.message.id == msg.id
            and e.interaction.component_type == hikari.ComponentType.TEXT_SELECT_MENU,
        )

    except asyncio.TimeoutError:
        await msg.edit("The menu timed out :c", components=[])

    else:
        animal = event.interaction.values[0]

        async with ctx.bot.d.client_session.get(
            f"https://some-random-api.com/animal/{animal}"
        ) as res:
            if not res.ok:
                await msg.edit(f"API returned a {res.status} status :c", components=[])

                return

            data = await res.json()

            embed = hikari.Embed(description=data["fact"], colour=0x3B9DFF)

            embed.set_image(data["image"])

            animal = animal.replace("_", " ")

            await msg.edit(f"Here's a {animal} for you! :3", embed=embed, components=[])


@fun_group.child
@lightbulb.command("meme", "Get a meme!")
@lightbulb.implements(lightbulb.SlashSubCommand)
async def meme_subcommand(ctx: lightbulb.SlashContext) -> None:
    async with ctx.bot.d.client_session.get("https://meme-api.com/gimme") as res:
        if not res.ok:
            await ctx.respond(
                f"API returned a {res.status} status :c",
                flags=hikari.MessageFlag.EPHEMERAL,
            )

            return

        data = await res.json()

        if data["nsfw"]:
            await ctx.respond(
                "Response was NSFW, couldn't send :c",
                flags=hikari.MessageFlag.EPHEMERAL,
            )

            return

        embed = hikari.Embed(colour=0x3B9DFF)

        embed.set_author(name=data["title"], url=data["postLink"])

        embed.set_image(data["url"])

        await ctx.respond(embed)


def load(bot: lightbulb.BotApp) -> None:
    bot.add_plugin(fun_plugin)
