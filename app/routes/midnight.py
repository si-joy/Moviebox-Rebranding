from flask import Blueprint, render_template, request
from app.services.tmdb import get_tmdb

midnight_bp = Blueprint("midnight", __name__, url_prefix="/midnight")


@midnight_bp.route("/")
def midnight():

    page = request.args.get("page", 1, type=int)
    media_type = request.args.get("type", "all")
    genre = request.args.get("genre", "")
    year = request.args.get("year", "")
    sort = request.args.get("sort", "popularity.desc")

    # Keep page within TMDB's normal pagination range
    page = max(1, min(page, 500))

    # ==========================================
    # GENRES
    # ==========================================

    movie_genres_data = get_tmdb(
        "genre/movie/list",
        {
            "language": "en-US"
        }
    )

    movie_genres = movie_genres_data.get("genres", [])

    tv_genres_data = get_tmdb(
        "genre/tv/list",
        {
            "language": "en-US"
        }
    )

    tv_genres = tv_genres_data.get("genres", [])

    # Merge genres without duplicates
    genre_map = {}

    for item in movie_genres + tv_genres:
        genre_map[item["id"]] = item["name"]

    genres = sorted(
        genre_map.items(),
        key=lambda item: item[1]
    )

    # ==========================================
    # DISCOVER PARAMS
    # ==========================================

    params = {
        "language": "en-US",
        "page": page,
        "sort_by": sort,
        "include_adult": "true"
    }

    if genre:
        params["with_genres"] = genre

    if year:
        if media_type == "tv":
            params["first_air_date_year"] = year
        else:
            params["primary_release_year"] = year

    # ==========================================
    # MOVIES
    # ==========================================

    movies = []
    movie_total_pages = 1
    movie_total_results = 0

    if media_type in ("all", "movie"):

        movie_data = get_tmdb(
            "discover/movie",
            params
        )

        movies = movie_data.get("results", [])

        movie_total_pages = movie_data.get(
            "total_pages",
            1
        )

        movie_total_results = movie_data.get(
            "total_results",
            0
        )

    # ==========================================
    # TV
    # ==========================================

    tv_shows = []
    tv_total_pages = 1
    tv_total_results = 0

    if media_type in ("all", "tv"):

        tv_params = {
            "language": "en-US",
            "page": page,
            "sort_by": sort,
            "include_adult": "true"
        }

        if genre:
            tv_params["with_genres"] = genre

        if year:
            tv_params["first_air_date_year"] = year

        tv_data = get_tmdb(
            "discover/tv",
            tv_params
        )

        tv_shows = tv_data.get(
            "results",
            []
        )

        tv_total_pages = tv_data.get(
            "total_pages",
            1
        )

        tv_total_results = tv_data.get(
            "total_results",
            0
        )

    # ==========================================
    # COMBINE RESULTS
    # ==========================================

    content = []

    if media_type == "movie":

        for movie in movies:
            movie["media_type"] = "movie"
            content.append(movie)

    elif media_type == "tv":

        for show in tv_shows:
            show["media_type"] = "tv"
            content.append(show)

    else:

        for movie in movies:
            movie["media_type"] = "movie"
            content.append(movie)

        for show in tv_shows:
            show["media_type"] = "tv"
            content.append(show)

        # Sort combined results
        if sort == "vote_average.desc":
            content.sort(
                key=lambda item: item.get(
                    "vote_average",
                    0
                ),
                reverse=True
            )

        elif sort == "vote_count.desc":
            content.sort(
                key=lambda item: item.get(
                    "vote_count",
                    0
                ),
                reverse=True
            )

        elif sort == "release_date.desc":

            def release_date(item):
                return (
                    item.get("release_date")
                    or item.get("first_air_date")
                    or ""
                )

            content.sort(
                key=release_date,
                reverse=True
            )

        else:
            content.sort(
                key=lambda item: item.get(
                    "popularity",
                    0
                ),
                reverse=True
            )

    # ==========================================
    # PAGINATION
    # ==========================================

    if media_type == "movie":
        total_pages = movie_total_pages
        total_results = movie_total_results

    elif media_type == "tv":
        total_pages = tv_total_pages
        total_results = tv_total_results

    else:
        total_pages = max(
            movie_total_pages,
            tv_total_pages
        )

        total_results = (
            movie_total_results +
            tv_total_results
        )

    total_pages = min(total_pages, 500)

    # ==========================================
    # YEARS
    # ==========================================

    years = list(
        range(
            2026,
            1970,
            -1
        )
    )

    return render_template(
        "pages/midnight.html",

        content=content,

        genres=genres,

        years=years,

        current_page=page,

        total_pages=total_pages,

        total_results=total_results,

        current_type=media_type,

        current_genre=genre,

        current_year=year,

        current_sort=sort
    )