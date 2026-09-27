from flask import (
    Blueprint,
    render_template
)

from app.services.nexstream import (
    get_movie_stream_url,
    get_tv_stream_url
)


player_bp = Blueprint(
    "player",
    __name__
)


@player_bp.route(
    "/movie-player/<int:movie_id>"
)
def movie_player(movie_id):

    stream_url = get_movie_stream_url(
        movie_id
    )

    return render_template(
        "pages/player.html",
        stream_url=stream_url
    )


@player_bp.route(
    "/tv-player/<int:tv_id>/<int:season>/<int:episode>"
)
def tv_player(
    tv_id,
    season,
    episode
):

    stream_url = get_tv_stream_url(
        tv_id,
        season,
        episode
    )

    return render_template(
        "pages/player.html",
        stream_url=stream_url
    )