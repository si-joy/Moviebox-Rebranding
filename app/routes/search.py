from flask import (
    Blueprint,
    request
)

from app.services.tmdb import get_tmdb


search_bp = Blueprint(
    "search",
    __name__
)


@search_bp.route("/api/search")
def search():

    query = request.args.get(
        "q",
        ""
    ).strip()

    if not query:
        return {
            "results": []
        }

    data = get_tmdb(
        "search/multi",
        {
            "language": "en-US",
            "query": query,
            "page": 1,
            "include_adult": False
        }
    )

    results = []

    seen = set()

    for item in data.get(
        "results",
        []
    ):

        media_type = item.get(
            "media_type"
        )

        if media_type not in [
            "movie",
            "tv"
        ]:
            continue

        item_id = item.get("id")

        if not item_id:
            continue

        unique_key = (
            media_type,
            item_id
        )

        if unique_key in seen:
            continue

        seen.add(unique_key)

        results.append({
            "id": item_id,
            "media_type": media_type,
            "title": (
                item.get("title")
                or item.get("name")
            ),
            "poster_path": item.get(
                "poster_path"
            ),
            "release_date": (
                item.get("release_date")
                or item.get(
                    "first_air_date"
                )
                or ""
            ),
            "overview": item.get(
                "overview"
            ),
            "vote_average": item.get(
                "vote_average",
                0
            )
        })

    return {
        "results": results[:10]
    }