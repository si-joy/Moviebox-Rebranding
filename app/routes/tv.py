from flask import Blueprint, render_template, request
from app.services.tmdb import get_tmdb

tv_bp = Blueprint("tv", __name__)

TMDB_PER_PAGE = 20
SITE_PER_PAGE = 24
MAX_TMDB_PAGE = 500


@tv_bp.route("/tv")
def tv_page():

    page = request.args.get("page", 1, type=int)

    if page < 1:
        page = 1

    # --------------------------------
    # Starting position
    # --------------------------------

    start_index = (page - 1) * SITE_PER_PAGE

    tmdb_page = (start_index // TMDB_PER_PAGE) + 1

    offset = start_index % TMDB_PER_PAGE

    # --------------------------------
    # Get first TMDB page
    # --------------------------------

    first_data = get_tmdb(
        "tv/popular",
        {
            "language": "en-US",
            "page": tmdb_page
        }
    )

    total_results = first_data.get(
        "total_results",
        0
    )

    # --------------------------------
    # TMDB maximum
    # 500 pages × 20 results
    # --------------------------------

    available_results = min(
        total_results,
        MAX_TMDB_PAGE * TMDB_PER_PAGE
    )

    total_pages = (
        available_results + SITE_PER_PAGE - 1
    ) // SITE_PER_PAGE

    # --------------------------------
    # Prevent invalid page
    # --------------------------------

    if total_pages > 0 and page > total_pages:

        page = total_pages

        start_index = (
            page - 1
        ) * SITE_PER_PAGE

        tmdb_page = (
            start_index // TMDB_PER_PAGE
        ) + 1

        offset = start_index % TMDB_PER_PAGE

        first_data = get_tmdb(
            "tv/popular",
            {
                "language": "en-US",
                "page": tmdb_page
            }
        )

    # --------------------------------
    # Collect enough results
    # --------------------------------

    shows = first_data.get(
        "results",
        []
    )

    while (
        len(shows) < offset + SITE_PER_PAGE
        and tmdb_page < MAX_TMDB_PAGE
    ):

        tmdb_page += 1

        next_data = get_tmdb(
            "tv/popular",
            {
                "language": "en-US",
                "page": tmdb_page
            }
        )

        next_shows = next_data.get(
            "results",
            []
        )

        if not next_shows:
            break

        shows.extend(next_shows)

    # --------------------------------
    # Get exactly 24 for this page
    # --------------------------------

    shows = shows[
        offset:offset + SITE_PER_PAGE
    ]

    # --------------------------------
    # Render
    # --------------------------------

    return render_template(
        "pages/tv.html",

        shows=shows,

        current_page=page,

        total_pages=total_pages
    )


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


@tv_bp.route(
    "/tv/<int:tv_id>/season/<int:season_number>"
)
def tv_season(tv_id, season_number):

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


@tv_bp.route(
    "/api/tv/<int:tv_id>/season/<int:season_number>"
)
def tv_season_api(tv_id, season_number):

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