from flask import Blueprint, render_template, request
from app.services.tmdb import get_tmdb, get_watch_providers

movies_bp = Blueprint("movies", __name__)

TMDB_PER_PAGE = 20
SITE_PER_PAGE = 24
MAX_TMDB_PAGE = 500


# =========================================================
# MOVIES CATALOG
# =========================================================

@movies_bp.route("/movies")
def movies_page():

    genre = request.args.get("genre", "").strip()
    year = request.args.get("year", "").strip()
    rating = request.args.get("rating", "").strip()
    provider = request.args.get("provider", "").strip()
    sort = request.args.get("sort", "popularity.desc").strip()
    page = request.args.get("page", 1, type=int)

    if page < 1:
        page = 1

    allowed_sorts = {
        "popularity.desc",
        "vote_average.desc",
        "release_date.desc"
    }

    if sort not in allowed_sorts:
        sort = "popularity.desc"

    # =====================================================
    # TMDB DISCOVER PARAMETERS
    # =====================================================

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
        base_params["watch_region"] = "US"

    # =====================================================
    # PAGINATION
    # =====================================================

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

    # =====================================================
    # PREVENT INVALID PAGE
    # =====================================================

    if total_pages > 0 and page > total_pages:

        page = total_pages

        start_index = (page - 1) * SITE_PER_PAGE

        tmdb_page = (
            start_index // TMDB_PER_PAGE
        ) + 1

        offset = start_index % TMDB_PER_PAGE

        first_data = get_tmdb(
            "discover/movie",
            {
                **base_params,
                "page": tmdb_page
            }
        )

    movies = first_data.get("results", [])

    # =====================================================
    # FETCH ADDITIONAL TMDB PAGE WHEN NEEDED
    # =====================================================

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

    movies = movies[
        offset:offset + SITE_PER_PAGE
    ]

    # =====================================================
    # FILTER DATA
    # =====================================================

    genre_data = get_tmdb(
        "genre/movie/list",
        {
            "language": "en-US"
        }
    )

    provider_data = get_watch_providers()

    providers = provider_data.get(
        "results",
        []
    )

    providers = sorted(
        providers,
        key=lambda provider: provider.get(
            "display_priority",
            999
        )
    )

    # =====================================================
    # RENDER
    # =====================================================

    return render_template(
        "pages/movies.html",

        movies=movies,

        genres=genre_data.get(
            "genres",
            []
        ),

        providers=providers,

        current_genre=genre,
        current_year=year,
        current_rating=rating,
        current_provider=provider,
        current_sort=sort,

        current_page=page,
        total_pages=total_pages
    )


# =========================================================
# MOVIE DETAIL PAGE
# =========================================================

@movies_bp.route("/movie/<int:movie_id>")
def movie_detail(movie_id):

    # =====================================================
    # MOVIE DETAILS
    # =====================================================

    movie = get_tmdb(
        f"movie/{movie_id}",
        {
            "language": "en-US",
            "append_to_response": "videos,credits,images"
        }
    )

    if not movie or movie.get("status_code") == 34:
        return "Movie not found", 404

    # =====================================================
    # TRAILER
    # =====================================================

    trailer = None

    videos = (
        movie.get("videos", {})
        .get("results", [])
    )

    # First try official YouTube trailer
    for video in videos:

        if (
            video.get("site") == "YouTube"
            and video.get("type") == "Trailer"
            and video.get("official") is True
        ):
            trailer = video
            break

    # Fallback to any YouTube trailer
    if not trailer:

        for video in videos:

            if (
                video.get("site") == "YouTube"
                and video.get("type") == "Trailer"
            ):
                trailer = video
                break

    # Fallback to any YouTube video
    if not trailer:

        for video in videos:

            if video.get("site") == "YouTube":
                trailer = video
                break

    # =====================================================
    # CAST
    # =====================================================

    credits = movie.get(
        "credits",
        {}
    )

    cast = credits.get(
        "cast",
        []
    )

    cast = cast[:12]

    # =====================================================
    # CREW
    # =====================================================

    crew = credits.get(
        "crew",
        []
    )

    directors = [
        person
        for person in crew
        if person.get("job") == "Director"
    ]

    writers = [
        person
        for person in crew
        if person.get("department") == "Writing"
        and person.get("job") in [
            "Screenplay",
            "Writer",
            "Story"
        ]
    ]

    # Remove duplicate people
    writer_ids = set()
    unique_writers = []

    for writer in writers:

        writer_id = writer.get("id")

        if writer_id not in writer_ids:

            writer_ids.add(writer_id)
            unique_writers.append(writer)

    writers = unique_writers[:5]

    # =====================================================
    # RECOMMENDATIONS
    # =====================================================

    recommendation_data = get_tmdb(
        f"movie/{movie_id}/recommendations",
        {
            "language": "en-US",
            "page": 1
        }
    )

    recommendations = recommendation_data.get(
        "results",
        []
    )

    recommendations = [
        item
        for item in recommendations
        if item.get("poster_path")
    ][:12]

    # =====================================================
    # SIMILAR MOVIES
    # =====================================================

    if not recommendations:

        similar_data = get_tmdb(
            f"movie/{movie_id}/similar",
            {
                "language": "en-US",
                "page": 1
            }
        )

        recommendations = similar_data.get(
            "results",
            []
        )

        recommendations = [
            item
            for item in recommendations
            if item.get("poster_path")
        ][:12]

    # =====================================================
    # WATCH PROVIDERS
    # =====================================================

    watch_data = get_tmdb(
        f"movie/{movie_id}/watch/providers",
        {}
    )

    watch_results = watch_data.get(
        "results",
        {}
    )

    # US is used as default because TMDB provider
    # availability is region based.
    watch_region = (
        watch_results.get("US")
        or {}
    )

    streaming = watch_region.get(
        "flatrate",
        []
    )

    rent = watch_region.get(
        "rent",
        []
    )

    buy = watch_region.get(
        "buy",
        []
    )

    # =====================================================
    # DIRECTOR
    # =====================================================

    director = (
        directors[0]
        if directors
        else None
    )

    # =====================================================
    # RENDER
    # =====================================================

    return render_template(
        "pages/movie-detail.html",

        movie=movie,

        trailer=trailer,

        cast=cast,

        director=director,

        writers=writers,

        recommendations=recommendations,

        streaming=streaming,

        rent=rent,

        buy=buy
    )