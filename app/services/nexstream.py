from flask import current_app


NEXSTREAM_BASE_URL = "https://api.codespecters.com/embed"


def get_movie_stream_url(movie_id):

    api_key = current_app.config[
        "NEXSTREAM_API_KEY"
    ]

    return (
        f"{NEXSTREAM_BASE_URL}/movie/"
        f"{movie_id}"
        f"?apikey={api_key}"
    )


def get_tv_stream_url(
    tv_id,
    season,
    episode
):

    api_key = current_app.config[
        "NEXSTREAM_API_KEY"
    ]

    return (
        f"{NEXSTREAM_BASE_URL}/tv/"
        f"{tv_id}/"
        f"{season}/"
        f"{episode}"
        f"?apikey={api_key}"
    )