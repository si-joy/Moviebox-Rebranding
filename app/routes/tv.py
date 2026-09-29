from flask import Blueprint, render_template, request
from app.services.tmdb import get_tmdb, get_watch_providers


tv_bp = Blueprint("tv", __name__)


TMDB_PER_PAGE = 20
SITE_PER_PAGE = 24
MAX_TMDB_PAGE = 500


# =========================================================
# TV CATALOG
# =========================================================

@tv_bp.route("/tv")
def tv_page():

    # =====================================================
    # CURRENT PAGE
    # =====================================================

    page = request.args.get(
        "page",
        1,
        type=int
    )

    if page < 1:
        page = 1


    # =====================================================
    # FILTERS
    # =====================================================

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


    # =====================================================
    # CALCULATE TMDB PAGE
    # =====================================================

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


    # =====================================================
    # TMDB DISCOVER PARAMETERS
    # =====================================================

    params = {
        "language": "en-US",
        "page": tmdb_page,
        "sort_by": sort,
        "include_adult": False,
        "vote_count.gte": 50,
    }


    # =====================================================
    # GENRE FILTER
    # =====================================================

    if genre:
        params["with_genres"] = genre


    # =====================================================
    # YEAR FILTER
    # =====================================================

    if year:
        params["first_air_date_year"] = year


    # =====================================================
    # RATING FILTER
    # =====================================================

    if rating:
        params["vote_average.gte"] = rating


    # =====================================================
    # STREAMING PLATFORM FILTER
    # =====================================================

    if provider:
        params["with_watch_providers"] = provider
        params["watch_region"] = "US"


    # =====================================================
    # FIRST TMDB REQUEST
    # =====================================================

    first_data = get_tmdb(
        "discover/tv",
        params
    )


    # =====================================================
    # TOTAL RESULTS
    # =====================================================

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


    # =====================================================
    # PROTECT AGAINST INVALID PAGE
    # =====================================================

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
            "discover/tv",
            params
        )


    # =====================================================
    # TV SHOWS
    # =====================================================

    shows = first_data.get(
        "results",
        []
    )


    # =====================================================
    # LOAD ADDITIONAL TMDB PAGES
    # =====================================================

    while (
        len(shows)
        < offset + SITE_PER_PAGE
        and tmdb_page < MAX_TMDB_PAGE
    ):

        tmdb_page += 1

        params["page"] = tmdb_page

        next_data = get_tmdb(
            "discover/tv",
            params
        )

        next_shows = next_data.get(
            "results",
            []
        )

        if not next_shows:
            break

        shows.extend(
            next_shows
        )


    # =====================================================
    # GET CURRENT 24 SHOWS
    # =====================================================

    shows = shows[
        offset:
        offset + SITE_PER_PAGE
    ]


    # =====================================================
    # TV GENRES
    # =====================================================

    genre_data = get_tmdb(
        "genre/tv/list",
        {
            "language": "en-US"
        }
    )

    genres = genre_data.get(
        "genres",
        []
    )


    # =====================================================
    # STREAMING PROVIDERS
    # =====================================================

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
    # RENDER TV PAGE
    # =====================================================

    return render_template(
        "pages/tv.html",

        shows=shows,

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


# =========================================================
# TV DETAIL
# =========================================================

@tv_bp.route("/tv/<int:tv_id>")
def tv_detail(tv_id):

    show = get_tmdb(
        f"tv/{tv_id}",
        {
            "language": "en-US",
            "append_to_response": "credits"
        }
    )


    if not show:
        return "TV show not found", 404


    return render_template(
        "pages/tv-detail.html",
        show=show
    )


# =========================================================
# TV SEASON
# =========================================================

@tv_bp.route(
    "/tv/<int:tv_id>/season/<int:season_number>"
)
def tv_season(
    tv_id,
    season_number
):

    show = get_tmdb(
        f"tv/{tv_id}",
        {
            "language": "en-US"
        }
    )


    if not show:
        return "TV show not found", 404


    season = get_tmdb(
        f"tv/{tv_id}/season/{season_number}",
        {
            "language": "en-US"
        }
    )


    if not season:
        return "Season not found", 404


    return render_template(
        "pages/episodes.html",
        show=show,
        season=season
    )


# =========================================================
# TV SEASON API
# =========================================================

@tv_bp.route(
    "/api/tv/<int:tv_id>/season/<int:season_number>"
)
def tv_season_api(
    tv_id,
    season_number
):

    data = get_tmdb(
        f"tv/{tv_id}/season/{season_number}",
        {
            "language": "en-US"
        }
    )


    return {
        "episodes": data.get(
            "episodes",
            []
        )
    }