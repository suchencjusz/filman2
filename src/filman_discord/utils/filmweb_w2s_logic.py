import asyncio
import random
import requests
import logging
import hikari

logger = logging.getLogger(__name__)

async def process_users(users):
    mentioned_users = [user.mention for user in users if user is not None]
    response = f"Mentioned {len(mentioned_users)} users:\n" + "\n".join(mentioned_users)
    
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
    
    movies_to_watch = []
    for filmweb_id, user in filmweb_ids.items():
        logger.debug(f"Fetching list of movies to watch for Filmweb ID: {filmweb_id}")
        r = requests.get(f"https://www.filmweb.pl/api/v1/user/{filmweb_id}/want2see/film")
        if r.status_code == 200:
            movie_entities = r.json()
            for movie in movie_entities:
                movie_id = movie.get("entity")
                movie_url = f"https://www.filmweb.pl/film/x-1-{movie_id}"
                movies_to_watch.append((movie_url, user))
                logger.debug(f"Added movie to list: {movie_url} from user: {user.id}")
        else:
            logger.error(f"Error fetching list of movies for Filmweb ID: {filmweb_id}, status: {r.status_code}")
    
    if movies_to_watch:
        selected_movie, selected_user = random.choice(movies_to_watch)
        response += f"\n\nSelected movie: {selected_movie} from {selected_user.mention}'s list"
        logger.info(f"Selected movie: {selected_movie} from {selected_user.id}'s list")
    else:
        response += "\n\nNo movies found to watch."
        logger.warning("No movies found to watch.")

    return response