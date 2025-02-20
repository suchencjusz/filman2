import logging
import random
from enum import Enum

import requests

logger = logging.getLogger(__name__)


class MediaType(Enum):
    FILM = "film"
    SERIAL = "serial"


async def fetch_filmweb_id(user: any) -> str | None:
    logger.debug(f"Fetching Filmweb ID for user: {user.id}")
    response = requests.get(
        f"http://filman_server:8000/filmweb/user/mapping/get",
        params={"discord_id": user.id},
    )
    if response.status_code == 200:
        filmweb_id = response.json().get("filmweb_id")
        if filmweb_id:
            logger.debug(f"Found Filmweb ID: {filmweb_id} for user: {user.id}")
            return filmweb_id
        else:
            logger.warning(f"No Filmweb ID found for user: {user.id}")
    else:
        logger.error(
            f"Error fetching Filmweb ID for user: {user.id}, status: {response.status_code}"
        )
    return None


async def fetch_media_to_watch(
    filmweb_id: str, media_type: MediaType
) -> dict[str, any] | None:
    logger.debug(f"Fetching list of media to watch for Filmweb ID: {filmweb_id}")
    response = requests.get(
        f"https://www.filmweb.pl/api/v1/user/{filmweb_id}/want2see/{media_type.value}",
        timeout=5,
    )
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(
            f"Error fetching list of media for Filmweb ID: {filmweb_id}, status: {response.status_code}"
        )
    return None


async def process_media(
    users: any, draw_common_media: bool = False, media_type: MediaType = MediaType.FILM
) -> str:
    mentioned_users = [user.mention for user in users if user is not None]
    logger.debug(f"Users: {mentioned_users}")

    filmweb_ids = {
        await fetch_filmweb_id(user): user for user in users if user is not None
    }
    filmweb_ids = {k: v for k, v in filmweb_ids.items() if k is not None}

    media_to_watch: dict[str, dict[str, any]] = {}
    for filmweb_id, user in filmweb_ids.items():
        media_entities = await fetch_media_to_watch(filmweb_id, media_type)
        if media_entities:
            for media in media_entities:
                media_id = media.get("entity")
                media_url = f"https://www.filmweb.pl/{media_type.value}/x-1-{media_id}"
                if media_id not in media_to_watch:
                    media_to_watch[media_id] = {"url": media_url, "users": set()}
                media_to_watch[media_id]["users"].add(user.id)
                logger.debug(
                    f"Added {media_type.value} to list: {media_url} from user: {user.id}"
                )

    common_media = [
        media for media in media_to_watch.values() if len(media["users"]) > 1
    ]

    response_url = ""
    response_mentions = ""

    if draw_common_media:
        if common_media:
            common_media_item = random.choice(common_media)
            user_mentions = ", ".join(
                [f"<@{user_id}>" for user_id in common_media_item["users"]]
            )
            response_url = common_media_item["url"]
            response_mentions = f"z listy {user_mentions}"
        else:
            if media_type == MediaType.FILM:
                response_url = "Brak wspólnych filmów."
            else:
                response_url = "Brak wspólnych seriali."
            response_mentions = ""
    else:
        uncommon_media = [
            media for media in media_to_watch.values() if len(media["users"]) == 1
        ]
        if uncommon_media:
            uncommon_media_item = random.choice(uncommon_media)
            user_mentions = ", ".join(
                [f"<@{user_id}>" for user_id in uncommon_media_item["users"]]
            )
            response_url = uncommon_media_item["url"]
            response_mentions = f"z listy {user_mentions}"
        else:
            if media_type == MediaType.FILM:
                response_url = "Brak filmów do obejrzenia."
            else:
                response_url = "Brak seriali do obejrzenia."
            response_mentions = ""

    response = f"{response_url} {response_mentions}"

    return response
