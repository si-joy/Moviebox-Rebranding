from flask import Blueprint, render_template, request
from app.services.tmdb import get_tmdb, get_watch_providers

movies_bp = Blueprint("movies", __name__)

TMDB_PER_PAGE = 20
SITE_PER_PAGE = 24
MAX_TMDB_PAGE = 500


@movies_bp.route("/movies")
def movies_page():
    genre = request.args.get("genre", "")
    year = request.args.get("year", "")
    rating = request.args.get("rating", "")
    provider = request.args.get("provider", "")
    sort = request.args.get("sort", "popularity.desc")
    page = request.args.get("page", 1, type=int)

    if page < 1:
        page = 1

    base_params = {
        "language": "en-US",
        "sort_by": sort,
        "include_adult": False,
        "vote_count.gte": 50
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

    providers = provider_data.get("results", [])

    providers = sorted(
        providers,
        key=lambda provider: provider.get(
            "display_priority",
            999
        )
    )

    return render_template(
        "pages/movies.html",
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

@movies_bp.route("/movie/<int:movie_id>")
def movie_detail(movie_id):

    movie = get_tmdb(
        f"movie/{movie_id}",
        {
            "language": "en-US",
            "append_to_response": "videos,credits"
        }
    )

    if not movie:
        return "Movie not found", 404

    trailer = None

    videos = movie.get(
        "videos",
        {}
    ).get(
        "results",
        []
    )

    for video in videos:

        if (
            video.get("site") == "YouTube"
            and video.get("type") == "Trailer"
            and video.get("official") is True
        ):
            trailer = video
            break

    return render_template(
        "pages/movie-detail.html",
        movie=movie,
        trailer=trailer
    )