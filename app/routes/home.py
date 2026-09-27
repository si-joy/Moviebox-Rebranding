from flask import Blueprint, render_template
from app.services.tmdb import get_tmdb, get_watch_providers

home_bp = Blueprint("home", __name__)


from flask import Blueprint, render_template
from app.services.tmdb import get_tmdb, get_watch_providers

home_bp = Blueprint("home", __name__)


@home_bp.route("/")
def home():

    popular_data = get_tmdb(
        "movie/popular",
        {
            "language": "en-US",
            "page": 1
        }
    )

    popular_movies = popular_data.get("results", [])


    movie_data = get_tmdb(
        "movie/popular",
        {
            "language": "en-US",
            "page": 2
        }
    )

    movies = movie_data.get("results", [])


    tv_data = get_tmdb(
        "tv/popular",
        {
            "language": "en-US",
            "page": 1
        }
    )

    tv_shows = tv_data.get("results", [])


    provider_data = get_watch_providers()
    
    print("PROVIDER DATA:", provider_data)
    
    providers = provider_data.get("results", [])
    
    print("PROVIDERS:", providers)

    providers = sorted(
        providers,
        key=lambda provider: provider.get(
            "display_priority",
            999
        )
    )


    return render_template(
        "pages/home.html",
        popular_movies=popular_movies[:12],
        movies=movies[:12],
        tv_shows=tv_shows[:12],
        providers=providers
    )

    # -----------------------------
    # Popular Movies
    # -----------------------------

    popular_data = get_tmdb(
        "movie/popular",
        {
            "language": "en-US",
            "page": 1
        }
    )

    popular_movies = popular_data.get("results", [])


    # -----------------------------
    # More Movies
    # -----------------------------

    movie_data = get_tmdb(
        "movie/popular",
        {
            "language": "en-US",
            "page": 2
        }
    )

    movies = movie_data.get("results", [])


    # -----------------------------
    # Popular TV Shows
    # -----------------------------

    tv_data = get_tmdb(
        "tv/popular",
        {
            "language": "en-US",
            "page": 1
        }
    )

    tv_shows = tv_data.get("results", [])


    # -----------------------------
    # Homepage
    # -----------------------------

    return render_template(
        "pages/home.html",

        popular_movies=popular_movies[:12],

        movies=movies[:12],

        tv_shows=tv_shows[:12]
    )