from flask import Blueprint, render_template, request
from app.services.tmdb import get_tmdb

midnight_bp = Blueprint("midnight", __name__, url_prefix="/midnight")


# =========================================================
# OPTIONAL: CUSTOM MIDNIGHT CATALOG (For Non-TMDB Items)
# =========================================================
CUSTOM_MIDNIGHT_ITEMS = [
    # {
    #     "id": "custom_1",
    #     "title": "Midnight Special Drama 1",
    #     "poster_path": "/static/images/sample.jpg",
    #     "media_type": "movie",
    #     "custom_stream_url": "https://doodstream.com/e/example",
    #     "vote_average": 8.5,
    #     "release_date": "2026-01-01"
    # }
]


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
    # GENRES (Movie + TV Combined)
    # ==========================================

    movie_genres_data = get_tmdb(
        "genre/movie/list",
        {"language": "en-US"}
    )
    movie_genres = movie_genres_data.get("genres", [])

    tv_genres_data = get_tmdb(
        "genre/tv/list",
        {"language": "en-US"}
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
    # DISCOVER PARAMS (TARGETED FOR ADULT/R-RATED)
    # ==========================================

    base_params = {
        "language": "en-US",
        "page": page,
        "sort_by": sort,
        "include_adult": "true",  # Enables adult search in TMDB
        "certification_country": "US",
        "certification.gte": "R", # Restricts output to R / NC-17 / Adult
    }

    if genre:
        base_params["with_genres"] = genre

    # ==========================================
    # MOVIES
    # ==========================================

    movies = []
    movie_total_pages = 1
    movie_total_results = 0

    if media_type in ("all", "movie"):
        movie_params = base_params.copy()

        if year:
            movie_params["primary_release_year"] = year

        movie_data = get_tmdb("discover/movie", movie_params)

        movies = movie_data.get("results", [])
        movie_total_pages = movie_data.get("total_pages", 1)
        movie_total_results = movie_data.get("total_results", 0)

    # ==========================================
    # TV SHOWS
    # ==========================================

    tv_shows = []
    tv_total_pages = 1
    tv_total_results = 0

    if media_type in ("all", "tv"):
        tv_params = base_params.copy()

        # TV shows don't support standard US certification in the same query key
        tv_params.pop("certification_country", None)
        tv_params.pop("certification.gte", None)

        if year:
            tv_params["first_air_date_year"] = year

        tv_data = get_tmdb("discover/tv", tv_params)

        tv_shows = tv_data.get("results", [])
        tv_total_pages = tv_data.get("total_pages", 1)
        tv_total_results = tv_data.get("total_results", 0)

    # ==========================================
    # COMBINE & FORMAT RESULTS
    # ==========================================

    content = []

    # Insert custom items on page 1 if applicable
    if page == 1 and CUSTOM_MIDNIGHT_ITEMS:
        for custom_item in CUSTOM_MIDNIGHT_ITEMS:
            if media_type == "all" or custom_item.get("media_type") == media_type:
                content.append(custom_item)

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

        # Sort combined results based on active filter
        if sort == "vote_average.desc":
            content.sort(
                key=lambda item: item.get("vote_average", 0),
                reverse=True
            )
        elif sort == "vote_count.desc":
            content.sort(
                key=lambda item: item.get("vote_count", 0),
                reverse=True
            )
        elif sort == "release_date.desc":
            def get_date(item):
                return item.get("release_date") or item.get("first_air_date") or ""
            content.sort(key=get_date, reverse=True)
        else:
            content.sort(
                key=lambda item: item.get("popularity", 0),
                reverse=True
            )

    # ==========================================
    # PAGINATION CALCULATIONS
    # ==========================================

    if media_type == "movie":
        total_pages = movie_total_pages
        total_results = movie_total_results
    elif media_type == "tv":
        total_pages = tv_total_pages
        total_results = tv_total_results
    else:
        total_pages = max(movie_total_pages, tv_total_pages)
        total_results = movie_total_results + tv_total_results

    total_pages = min(total_pages, 500)

    # Years dropdown array (Dynamic up to current year 2026)
    years = list(range(2026, 1970, -1))

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