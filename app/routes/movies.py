from flask import Blueprint, render_template, request
from app.services.tmdb import get_tmdb

movies_bp = Blueprint("movies", __name__)

TMDB_PER_PAGE = 20
SITE_PER_PAGE = 24
MAX_TMDB_PAGE = 500


@movies_bp.route("/movies")
def movies_page():

    genre = request.args.get("genre", "")
    year = request.args.get("year", "")
    rating = request.args.get("rating", "")
    sort = request.args.get("sort", "popularity.desc")

    page = request.args.get("page", 1, type=int)

    if page < 1:
        page = 1

    # --------------------------------
    # Base TMDB parameters
    # --------------------------------

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

    # --------------------------------
    # Calculate TMDB page + offset
    # --------------------------------

    start_index = (page - 1) * SITE_PER_PAGE

    tmdb_page = (start_index // TMDB_PER_PAGE) + 1

    offset = start_index % TMDB_PER_PAGE

    # --------------------------------
    # Get first TMDB page
    # --------------------------------

    first_data = get_tmdb(
        "discover/movie",
        {
            **base_params,
            "page": tmdb_page
        }
    )

    total_results = first_data.get("total_results", 0)

    # --------------------------------
    # TMDB only exposes up to 500 pages
    # = maximum 10,000 accessible results
    # --------------------------------

    available_results = min(
        total_results,
        MAX_TMDB_PAGE * TMDB_PER_PAGE
    )

    total_pages = (
        available_results + SITE_PER_PAGE - 1
    ) // SITE_PER_PAGE

    # --------------------------------
    # If requested page is too high
    # --------------------------------

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

    # --------------------------------
    # Collect enough TMDB results
    # to create 24 movies
    # --------------------------------

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

    # --------------------------------
    # Take exactly 24 movies
    # starting from the correct offset
    # --------------------------------

    movies = movies[
        offset:offset + SITE_PER_PAGE
    ]

    # --------------------------------
    # Get movie genres
    # --------------------------------

    genre_data = get_tmdb(
        "genre/movie/list",
        {
            "language": "en-US"
        }
    )

    # --------------------------------
    # Render page
    # --------------------------------

    return render_template(
        "pages/movies.html",

        movies=movies,

        genres=genre_data.get(
            "genres",
            []
        ),

        current_genre=genre,
        current_year=year,
        current_rating=rating,
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