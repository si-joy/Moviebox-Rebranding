from flask import Blueprint, render_template
from app.services.tmdb import get_tmdb, get_watch_providers


home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def home():

    # ==========================================
    # HERO / POPULAR MOVIES
    # ==========================================

    popular_data = get_tmdb(
        "movie/popular",
        {
            "language": "en-US",
            "page": 1
        }
    )

    popular_movies = popular_data.get("results", [])


    # ==========================================
    # MORE MOVIES
    # ==========================================

    movie_data = get_tmdb(
        "movie/popular",
        {
            "language": "en-US",
            "page": 2
        }
    )

    movies = movie_data.get("results", [])


    # ==========================================
    # POPULAR TV
    # ==========================================

    tv_data = get_tmdb(
        "tv/popular",
        {
            "language": "en-US",
            "page": 1
        }
    )

    tv_shows = tv_data.get("results", [])


    # ==========================================
    # STREAMING PROVIDERS
    # ==========================================

    provider_data = get_watch_providers()

    providers = provider_data.get("results", [])

    providers = sorted(
        providers,
        key=lambda provider: provider.get(
            "display_priority",
            999
        )
    )


    # ==========================================
    # HOMEPAGE
    # ==========================================

    return render_template(
        "pages/home.html",
        popular_movies=popular_movies[:8],
        movies=movies[:12],
        tv_shows=tv_shows[:12],
        providers=providers
    )