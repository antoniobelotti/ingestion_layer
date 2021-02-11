import json
import logging
import sys

from AzureDataLake import AzureDataLake

from get_srobble_data import download_scrobble_data
from harvest_users import snowball_sampling
from settings import *

logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)

if __name__ == '__main__':
    dl = AzureDataLake(STORAGE_ACCOUNT_NAME, STORAGE_ACCOUNT_KEY, CONTAINER_NAME, "testNewLib")

    try:
        sync_file = dl.retrieve_json("/user_info/sync.json")
        # if this succeeds, we assume scrobble_data dir to already exists
    except Exception:
        # file does not exists
        dl.mkdir("/user_info")
        sync_file = {SNOWBALL_STARTING_USER: 0}
        dl.store(json.dumps(sync_file), "/user_info/sync.json", overwrite=True)

        # also create the scrobble_data dir
        dl.mkdir("/scrobble_data")

    for chunk_progressive, user_chunk in enumerate(snowball_sampling()):
        if len(dl.ls("/scrobble_data/")) >= MIN_TARGET_USERS:
            logging.info(f"Done. Downloaded {MIN_TARGET_USERS} users data")
            break

        logging.info(f"chunk {chunk_progressive + 1}")
        if (chunk_progressive + 1) > sync_file[SNOWBALL_STARTING_USER]:
            logging.info(f"Downloading chunk {chunk_progressive + 1}")
            # download this users chunk data
            skipped = download_scrobble_data(dl, user_chunk, PERIOD_START_UTS, PERIOD_END_UTS)
            logging.info(f"Successfully downloaded {USERS_CHUNK_SIZE -skipped}/{USERS_CHUNK_SIZE} users data")

            # update sync file
            sync_file[SNOWBALL_STARTING_USER] += 1
            dl.store(json.dumps(sync_file), filename="user_info/sync.json", overwrite=True)
        else:
            logging.info(f"Skipping chunk {chunk_progressive + 1}")