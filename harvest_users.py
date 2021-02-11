import logging
import sys

from settings import SNOWBALL_STARTING_USER, USERS_CHUNK_SIZE
from utils import EndpointBuilder, download_from

logging.basicConfig(level=logging.INFO)


def get_friends_for(username):
    result = []
    current_page = 1
    available_pages = 9999999999
    eb = EndpointBuilder("user.getFriends") \
        .param("user", username) \
        .param("recenttraks", False)

    while current_page <= available_pages:
        endpoint = eb.param("page", current_page).build()
        ds = download_from(endpoint)

        if ds.get("error", False):
            return []

        for friend in ds["friends"]["user"]:
            if friend["type"] == "user":
                if len(friend["realname"]) < 40:
                    result.append({
                        "name": friend["name"],
                        "realname": friend["realname"],
                        "country": friend["country"],
                        "registered": friend["registered"]
                    })
        available_pages = int(ds["friends"]["@attr"]["totalPages"])
        current_page += 1

    return result


def snowball_sampling(username=SNOWBALL_STARTING_USER):
    logging.info("Starting snowball sampling")

    friends = get_friends_for(username)
    if len(friends) == 0:
        logging.fatal("Entry-user for snowball sampling does not have any friend")
        sys.exit(1)

    res = friends
    for friend in friends:
        while len(res) > USERS_CHUNK_SIZE:
            yield res[:USERS_CHUNK_SIZE]
            res = res[USERS_CHUNK_SIZE:]

        res += get_friends_for(friend["name"])
