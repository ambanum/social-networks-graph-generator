from pathlib import Path
import tempfile

TMP_DIR = Path(tempfile.gettempdir())

PACKAGE_INSTALL_DIR = Path(__file__).parent

SNSCRAPE_TO_API = {
    "username": "name",
    "displayname": "screen_name",
    "created": "created_at",
    "followersCount": "followers_count",
    "friendsCount": "friends_count",
    "statusesCount": "statuses_count",
    "favouritesCount": "favourites_count",
    "listedCount": "listed_count",
}
