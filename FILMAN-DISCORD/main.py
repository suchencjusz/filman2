import hikari
import lightbulb
import aiohttp

from hikari import Intents
from typing import Optional

# INTENTS = Intents.GUILD_MEMBERS | Intents.GUILDS

bot = lightbulb.BotApp(
    "MTE4MjM3MTY1ODM0NzA2NTM5NA.Gr7OHu.Y3PW4Dl98nLZAzAw1eJfvAzpushE3GXyM0qAX8",
    intents=hikari.Intents.ALL,
    banner=None,
)


@bot.listen()
async def on_starting(_: hikari.StartingEvent) -> None:
    bot.d.client_session = aiohttp.ClientSession()


@bot.listen()
async def on_stopping(_: hikari.StoppingEvent) -> None:
    await bot.d.client_session.close()


@bot.command
@lightbulb.command("ping", description="The bot's ping.")
@lightbulb.implements(lightbulb.SlashCommand)
async def ping(ctx: lightbulb.SlashContext) -> None:
    await ctx.respond(f"Pong! Latency: {bot.heartbeat_latency * 1000:.2f}ms.")


bot.load_extensions_from("./endpoints/")

if __name__ == "__main__":
    bot.run()
