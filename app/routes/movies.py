from flask import Blueprint, render_template, request
from app.services.tmdb import get_tmdb, get_watch_providers


movies_bp = Blueprint("movies", __name__)


TMDB_PER_PAGE = 20
SITE_PER_PAGE = 24
MAX_TMDB_PAGE = 500


@movies_bp.route("/movies")
def movies_page():

    # =========================================================
    # CURRENT PAGE
    # =========================================================

    page = request.args.get(
        "page",
        1,
        type=int
    )

    if page < 1:
        page = 1


    # =========================================================
    # FILTERS
    # =========================================================

    genre = request.args.get(
        "genre",
        ""
    )

    year = request.args.get(
        "year",
        ""
    )

    rating = request.args.get(
        "rating",
        ""
    )

    provider = request.args.get(
        "provider",
        ""
    )

    sort = request.args.get(
        "sort",
        "popularity.desc"
    )


    # =========================================================
    # CALCULATE TMDB PAGE
    # =========================================================

    start_index = (
        (page - 1)
        * SITE_PER_PAGE
    )

    tmdb_page = (
        start_index
        // TMDB_PER_PAGE
    ) + 1

    offset = (
        start_index
        % TMDB_PER_PAGE
    )


    # =========================================================
    # TMDB DISCOVER PARAMETERS
    # =========================================================

    params = {
        "language": "en-US",
        "page": tmdb_page,
        "sort_by": sort,
        "include_adult": False,
        "vote_count.gte": 50,
    }


    # Genre
    if genre:
        params["with_genres"] = genre


    # Year
    if year:
        params["primary_release_year"] = year


    # Rating
    if rating:
        params["vote_average.gte"] = rating


    # Streaming Platform
    if provider:
        params["with_watch_providers"] = provider
        params["watch_region"] = "US"


    # =========================================================
    # FIRST TMDB REQUEST
    # =========================================================

    first_data = get_tmdb(
        "discover/movie",
        params
    )


    # =========================================================
    # TOTAL RESULTS
    # =========================================================

    total_results = first_data.get(
        "total_results",
        0
    )


    available_results = min(
        total_results,
        MAX_TMDB_PAGE * TMDB_PER_PAGE
    )


    total_pages = (
        available_results
        + SITE_PER_PAGE
        - 1
    ) // SITE_PER_PAGE


    # =========================================================
    # PROTECT AGAINST INVALID PAGE
    # =========================================================

    if (
        total_pages > 0
        and page > total_pages
    ):

        page = total_pages

        start_index = (
            (page - 1)
            * SITE_PER_PAGE
        )

        tmdb_page = (
            start_index
            // TMDB_PER_PAGE
        ) + 1

        offset = (
            start_index
            % TMDB_PER_PAGE
        )

        params["page"] = tmdb_page

        first_data = get_tmdb(
            "discover/movie",
            params
        )


    # =========================================================
    # MOVIES
    # =========================================================

    movies = first_data.get(
        "results",
        []
    )


    # =========================================================
    # LOAD ADDITIONAL TMDB PAGES
    #
    # Needed because:
    # TMDB = 20 results/page
    # Website = 24 results/page
    # =========================================================

    while (
        len(movies)
        < offset + SITE_PER_PAGE
        and tmdb_page < MAX_TMDB_PAGE
    ):

        tmdb_page += 1

        params["page"] = tmdb_page

        next_data = get_tmdb(
            "discover/movie",
            params
        )

        next_movies = next_data.get(
            "results",
            []
        )

        if not next_movies:
            break

        movies.extend(
            next_movies
        )


    # =========================================================
    # GET CURRENT 24 MOVIES
    # =========================================================

    movies = movies[
        offset:
        offset + SITE_PER_PAGE
    ]


    # =========================================================
    # GENRES
    # =========================================================

    genre_data = get_tmdb(
        "genre/movie/list",
        {
            "language": "en-US"
        }
    )

    genres = genre_data.get(
        "genres",
        []
    )


    # =========================================================
    # STREAMING PROVIDERS
    # =========================================================

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


    # =========================================================
    # RENDER PAGE
    # =========================================================

    return render_template(
        "pages/movies.html",

        movies=movies,

        genres=genres,

        providers=providers,

        current_page=page,

        total_pages=total_pages,

        current_genre=genre,

        current_year=year,

        current_rating=rating,

        current_provider=provider,

        current_sort=sort
    )


# =============================================================
# MOVIE DETAIL
# =============================================================

@movies_bp.route("/movie/<int:movie_id>")
def movie_detail(movie_id):

    movie = get_tmdb(
        f"movie/{movie_id}",
        {
            "language": "en-US",
            "append_to_response":
                "videos,credits,recommendations"
        }
    )


    if not movie:
        return "Movie not found", 404


    # =========================================================
    # TRAILER
    # =========================================================

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
            video.get("site")
            == "YouTube"
            and
            video.get("type")
            == "Trailer"
            and
            video.get("official")
            is True
        ):

            trailer = video

            break


    # =========================================================
    # CREDITS
    # =========================================================

    credits = movie.get(
        "credits",
        {}
    )

    crew = credits.get(
        "crew",
        []
    )

    cast = credits.get(
        "cast",
        []
    )


    # =========================================================
    # DIRECTOR
    # =========================================================

    director = next(
        (
            person
            for person in crew
            if person.get("job")
            == "Director"
        ),
        None
    )


    # =========================================================
    # WRITERS
    # =========================================================

    writers = [
        person
        for person in crew
        if person.get("department")
        == "Writing"
        and person.get("job")
        in (
            "Writer",
            "Screenplay",
            "Story"
        )
    ]


    # =========================================================
    # RECOMMENDATIONS
    # =========================================================

    recommendations = (
        movie.get(
            "recommendations",
            {}
        )
        .get(
            "results",
            []
        )
    )


    # =========================================================
    # RENDER
    # =========================================================

    return render_template(
        "pages/movie-detail.html",

        movie=movie,

        trailer=trailer,

        director=director,

        writers=writers[:5],

        cast=cast[:12],

        recommendations=
            recommendations[:12]
    )