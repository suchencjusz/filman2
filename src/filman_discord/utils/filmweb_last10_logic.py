import hikari
import lightbulb

def last10(media: list, typ: str) -> hikari.Embed:
    


# movies = sorted(movies, key=lambda x: datetime.strptime(x["date"], "%Y-%m-%dT%H:%M:%S"), reverse=True)

#         if len(movies) == 0:
#             embed = hikari.Embed(
#                 title=f"Nie oceniono jeszcze żadnych filmów!",
#                 colour=0xFF4400,
#                 timestamp=datetime.now().astimezone(),
#             )
#             embed.set_footer(
#                 text=f"Requested by {ctx.author}",
#                 icon=ctx.author.display_avatar_url,
#             )
#             await ctx.respond(embed)
#             return

#         # to do: movies != 0

#         if len(movies) > 10:
#             movies = movies[0:25]
#         else:
#             movies = movies[0:len(movies)]

#     embed = hikari.Embed(
#         title=f"Ostatnio ocenione filmy",
#         colour=0xFFC200,
#         timestamp=datetime.now().astimezone(),
#     )

#     temp_star_list = ""

#     for movie in movies:
#         temp_star_list += f"{star_emoji_counter(movie['rate'])} {movie[typ]['title']} ({movie[typ]['year']})\n"

#     embed.add_field(
#         name="Filmy",
#         value=temp_star_list,
#         inline=False,
#     )


#     embed.set_footer(
#         text=f"Requested by {ctx.author}",
#         icon=ctx.author.display_avatar_url,
#     )

#     await ctx.respond(embed)
