import lightbulb

plugin = lightbulb.Plugin(name="ping")


@plugin.command()
@lightbulb.check(lightbulb.owner_only)
@lightbulb.implements(lightbulb.PrefixCommand, lightbulb.SlashCommand)
async def ping(ctx: lightbulb.Context) -> None:
    """Ping the bot."""
    await ctx.respond(f"Pong! {round(ctx.bot.latency * 1000)}ms")


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(plugin)


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin(plugin)
