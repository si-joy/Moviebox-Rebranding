import requests
from flask import current_app


TMDB_BASE_URL = "https://api.themoviedb.org/3"


def get_tmdb(endpoint, params=None):

    if params is None:
        params = {}

    api_key = current_app.config["TMDB_API_KEY"]

    params = {
        **params,
        "api_key": api_key
    }

    url = f"{TMDB_BASE_URL}/{endpoint}"

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        print("TMDB URL:", response.url)
        print("TMDB STATUS:", response.status_code)

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:

        print("TMDB ERROR:", error)

        return {}


# =========================================
# MOVIE WATCH PROVIDERS
# =========================================

def get_watch_providers():

    return get_tmdb(
        "watch/providers/movie",
        {
            "language": "en-US",
            "watch_region": "US"
        }
    )


# =========================================
# TV WATCH PROVIDERS
# =========================================

def get_tv_watch_providers():

    return get_tmdb(
        "watch/providers/tv",
        {
            "language": "en-US",
            "watch_region": "US"
        }
    )