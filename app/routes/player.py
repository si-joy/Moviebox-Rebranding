from flask import Blueprint, render_template, request
from app.services.tmdb import get_tmdb


player_bp = Blueprint("player", __name__)


# =========================================================
# STREAMING SERVERS
# =========================================================

SERVERS = {

    # -----------------------------------------------------
    # 1. VidSrc.me
    # -----------------------------------------------------
    "vidsrc_me": {
        "name": "VidSrc.me",

        "movie":
            "https://vidsrc.me/embed/movie/{id}",

        "tv":
            "https://vidsrc.me/embed/tv/{id}/{season}/{episode}"
    },


    # -----------------------------------------------------
    # 2. CineSrc
    # -----------------------------------------------------
    "cinesrc": {
        "name": "CineSrc",

        "movie":
            "https://cinesrc.st/embed/movie/{id}",

        "tv":
            "https://cinesrc.st/embed/tv/{id}?s={season}&e={episode}"
    },


    # -----------------------------------------------------
    # 3. VidSrc.to
    # -----------------------------------------------------
    "vidsrc_to": {
        "name": "VidSrc.to",

        "movie":
            "https://vidsrc.to/embed/movie/{id}",

        "tv":
            "https://vidsrc.to/embed/tv/{id}/{season}/{episode}"
    },


    # -----------------------------------------------------
    # 4. VidLink
    # -----------------------------------------------------
    "vidlink": {
        "name": "VidLink",

        "movie":
            "https://vidlink.pro/movie/{id}",

        "tv":
            "https://vidlink.pro/tv/{id}/{season}/{episode}"
    },


    # -----------------------------------------------------
    # 5. VidCore
    # -----------------------------------------------------
    "vidcore": {
        "name": "VidCore",

        "movie":
            "https://vidcore.io/movie/{id}",

        "tv":
            "https://vidcore.io/tv/{id}/{season}/{episode}"
    }

}


# =========================================================
# MOVIE PLAYER
# =========================================================

@player_bp.route("/movie-player/<int:movie_id>")
def movie_player(movie_id):

    # Get selected server
    server_key = request.args.get(
        "server",
        "vidsrc_me"
    )

    # Validate server
    selected_server = SERVERS.get(
        server_key,
        SERVERS["vidsrc_me"]
    )

    # Build stream URL
    stream_url = selected_server["movie"].format(
        id=movie_id
    )

    # Get movie information from TMDB
    movie = get_tmdb(
        f"movie/{movie_id}",
        {
            "language": "en-US",
            "append_to_response": "recommendations"
        }
    )

    # Recommendations
    recommendations = []

    if movie:

        recommendations = (
            movie
            .get("recommendations", {})
            .get("results", [])
        )

    # Render player
    return render_template(
        "pages/player.html",

        stream_url=stream_url,

        content_id=movie_id,
        content_type="movie",

        servers=SERVERS,
        current_server=server_key,

        movie=movie,
        recommendations=recommendations[:8]
    )


# =========================================================
# TV PLAYER
# =========================================================

@player_bp.route(
    "/tv-player/<int:tv_id>/<int:season>/<int:episode>"
)
def tv_player(tv_id, season, episode):

    # Get selected server
    server_key = request.args.get(
        "server",
        "vidsrc_me"
    )

    # Validate server
    selected_server = SERVERS.get(
        server_key,
        SERVERS["vidsrc_me"]
    )

    # Build TV stream URL
    stream_url = selected_server["tv"].format(
        id=tv_id,
        season=season,
        episode=episode
    )

    # Get TV show information from TMDB
    show = get_tmdb(
        f"tv/{tv_id}",
        {
            "language": "en-US",
            "append_to_response": "recommendations"
        }
    )

    # Recommendations
    recommendations = []

    if show:

        recommendations = (
            show
            .get("recommendations", {})
            .get("results", [])
        )

    # Render player
    return render_template(
        "pages/player.html",

        stream_url=stream_url,

        content_id=tv_id,
        content_type="tv",

        season=season,
        episode=episode,

        servers=SERVERS,
        current_server=server_key,

        movie=show,
        recommendations=recommendations[:8]
    )