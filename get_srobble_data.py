import json
import logging

from tqdm import tqdm

from utils import EndpointBuilder, download_from

logging.basicConfig(level=logging.INFO)


def get_user_tracks_durations(user, period="overall"):
    """ https://www.last.fm/api/show/user.getTopTracks """

    user_songs_durations = {}
    eb = EndpointBuilder("user.gettoptracks").param("user", user).param("limit", 1000).param("period", period)
    last_page = 1110000000000000
    current_page = 1
    while current_page < last_page:
        endpoint = eb.param("page", current_page).build()
        response = download_from(endpoint)

        for track_info in response["toptracks"]["track"]:
            key = f"{track_info['name']}{track_info['artist']['name']}"
            user_songs_durations[key] = int(track_info["duration"])
        current_page += 1
        last_page = int(response["toptracks"]["@attr"]["totalPages"])
    return user_songs_durations


def clean_track_data(data, user_songs_durations):
    key = f"{data['name']}{data['artist']['#text']}"
    duration = user_songs_durations.get(key, 0)

    if duration == 0:
        # this track data is useless
        raise RuntimeError()

    return {
        "mbid": data["mbid"],
        "name": data["name"],
        "image_url": data["image"][3]["#text"],
        "artist": {
            "mbid": data["artist"]["mbid"],
            "name": data["artist"]["#text"]
        },
        "album": data["album"],
        "started_listening": int(data["date"]["uts"]),
        "track_duration": duration
    }


def download_user_scrobble_data(user_info, period_start, period_end):
    # download songs durations (of songs user has listened in the last 3month)
    durations = get_user_tracks_durations(user_info["name"], period="3month")

    eb = EndpointBuilder("user.getrecenttracks") \
        .param("user", user_info["name"]) \
        .param("limit", 200) \
        .param("page", 0) \
        .param("from", period_start) \
        .param("to", period_end)

    result = {"user_info": user_info, "tracks": []}

    current_page = 1
    last_page = 1000000000000
    while current_page <= last_page:
        endpoint = eb.update_param("page", current_page).build()

        page_data = download_from(endpoint)
        for track in page_data["recenttracks"]["track"]:
            try:
                result["tracks"].append(clean_track_data(track, durations))
            except:
                # some crucial data is missing in the track scrobble
                continue

        last_page = int(page_data["recenttracks"]["@attr"]["totalPages"])
        current_page += 1

    if len(result["tracks"]) == 0:
        return None
    return result


def download_scrobble_data(dlc, users, period_start, period_end):
    skipped = 0
    for user_info in tqdm(users):
        try:
            result = download_user_scrobble_data(user_info, period_start, period_end)
        except:
            result = None

        if result is None:
            # this user scrobble data is trash :)
            skipped += 1
            continue

        filename = f"u{user_info['name'].strip().lower()[:10]}"
        try:
            dlc.store(json.dumps(result), f"/scrobble_data/{filename}.json", overwrite=True)
        except RuntimeError:
            skipped += 1
            pass

    return skipped
