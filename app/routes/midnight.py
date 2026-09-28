from flask import Blueprint, render_template, request
from app.services.tmdb import get_tmdb, get_watch_providers

midnight_bp = Blueprint("midnight", __name__)

TMDB_PER_PAGE = 20
SITE_PER_PAGE = 24
MAX_TMDB_PAGE = 500


@midnight_bp.route("/midnight")
def midnight_page():
    genre = request.args.get("genre", "")
    year = request.args.get("year", "")
    rating = request.args.get("rating", "")
    provider = request.args.get("provider", "")
    sort = request.args.get("sort", "popularity.desc")
    page = request.args.get("page", 1, type=int)

    if page < 1:
        page = 1

    # include_adult: True set kora hoyeche
    base_params = {
        "language": "en-US",
        "sort_by": sort,
        "include_adult": True,
        "vote_count.gte": 10
    }

    if genre:
        base_params["with_genres"] = genre

    if year:
        base_params["primary_release_year"] = year

    if rating:
        base_params["vote_average.gte"] = rating

    if provider:
        base_params["with_watch_providers"] = provider

    start_index = (page - 1) * SITE_PER_PAGE
    tmdb_page = (start_index // TMDB_PER_PAGE) + 1
    offset = start_index % TMDB_PER_PAGE

    first_data = get_tmdb(
        "discover/movie",
        {
            **base_params,
            "page": tmdb_page
        }
    )

    total_results = first_data.get("total_results", 0)

    available_results = min(
        total_results,
        MAX_TMDB_PAGE * TMDB_PER_PAGE
    )

    total_pages = (
        available_results + SITE_PER_PAGE - 1
    ) // SITE_PER_PAGE

    if total_pages > 0 and page > total_pages:
        page = total_pages

        start_index = (page - 1) * SITE_PER_PAGE
        tmdb_page = (start_index // TMDB_PER_PAGE) + 1
        offset = start_index % TMDB_PER_PAGE

        first_data = get_tmdb(
            "discover/movie",
            {
                **base_params,
                "page": tmdb_page
            }
        )

    movies = first_data.get("results", [])

    while (
        len(movies) < offset + SITE_PER_PAGE
        and tmdb_page < MAX_TMDB_PAGE
    ):
        tmdb_page += 1

        next_data = get_tmdb(
            "discover/movie",
            {
                **base_params,
                "page": tmdb_page
            }
        )

        next_movies = next_data.get("results", [])

        if not next_movies:
            break

        movies.extend(next_movies)

    movies = movies[offset:offset + SITE_PER_PAGE]

    genre_data = get_tmdb(
        "genre/movie/list",
        {
            "language": "en-US"
        }
    )

    provider_data = get_watch_providers()
    providers = sorted(
        provider_data.get("results", []),
        key=lambda provider: provider.get("display_priority", 999)
    )

    return render_template(
        "pages/midnight.html",
        movies=movies,
        genres=genre_data.get("genres", []),
        providers=providers,
        current_genre=genre,
        current_year=year,
        current_rating=rating,
        current_provider=provider,
        current_sort=sort,
        current_page=page,
        total_pages=total_pages
    )