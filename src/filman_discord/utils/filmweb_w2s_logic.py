import asyncio
import random
import requests
import logging
import hikari


logger = logging.getLogger(__name__)


async def process_users(users, draw_common_movie=False) -> hikari.Embed:
    mentioned_users = [user.mention for user in users if user is not None]
    response = f"Oznaczono {len(mentioned_users)} użytkowników:\n" + "\n".join(mentioned_users)

    logger.debug(f"Users: {mentioned_users}")

    filmweb_ids = {}
    for user in users:
        if user is not None:
            logger.debug(f"Fetching Filmweb ID for user: {user.id}")
            r = requests.get(f"http://filman_server:8000/filmweb/user/mapping/get", params={"discord_id": user.id})
            if r.status_code == 200:
                filmweb_id = r.json().get("filmweb_id")
                if filmweb_id:
                    filmweb_ids[filmweb_id] = user
                    logger.debug(f"Found Filmweb ID: {filmweb_id} for user: {user.id}")
                else:
                    logger.warning(f"No Filmweb ID found for user: {user.id}")
            else:
                logger.error(f"Error fetching Filmweb ID for user: {user.id}, status: {r.status_code}")

    movies_to_watch = {}
    for filmweb_id, user in filmweb_ids.items():
        logger.debug(f"Fetching list of movies to watch for Filmweb ID: {filmweb_id}")
        r = requests.get(f"https://www.filmweb.pl/api/v1/user/{filmweb_id}/want2see/film")
        if r.status_code == 200:
            movie_entities = r.json()
            for movie in movie_entities:
                movie_id = movie.get("entity")
                movie_url = f"https://www.filmweb.pl/film/x-1-{movie_id}"
                if movie_id not in movies_to_watch:
                    movies_to_watch[movie_id] = {"url": movie_url, "users": set()}
                movies_to_watch[movie_id]["users"].add(user.id)
                logger.debug(f"Added movie to list: {movie_url} from user: {user.id}")
        else:
            logger.error(f"Error fetching list of movies for Filmweb ID: {filmweb_id}, status: {r.status_code}")

    common_movies = [movie for movie in movies_to_watch.values() if len(movie["users"]) > 1]

    if draw_common_movie:
        if common_movies:
            common_movie = random.choice(common_movies)
            user_mentions = ", ".join([f"<@{user_id}>" for user_id in common_movie["users"]])
            response += f"\nCommon movie to watch: {common_movie['url']} (added by {user_mentions})"
        else:
            response += "\nNo common movies found."
    else:
        uncommon_movies = [movie for movie in movies_to_watch.values() if len(movie["users"]) == 1]
        if uncommon_movies:
            uncommon_movie = random.choice(uncommon_movies)
            user_mentions = ", ".join([f"<@{user_id}>" for user_id in uncommon_movie["users"]])
            response += f"\nUncommon movie to watch: {uncommon_movie['url']} (added by {user_mentions})"
        else:
            response += "\nNo uncommon movies found."

    #todo: fix it 
    response_embed = hikari.Embed(
        title="Movies to watch",
        description=response,
        color=0xFFC200,
    )

    return response
