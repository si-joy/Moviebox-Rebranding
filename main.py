import os
import requests

from flask import Flask, render_template, request
from dotenv import load_dotenv


# =========================================================
# SETUP
# =========================================================

load_dotenv()

app = Flask(__name__)

TMDB_API_KEY = os.getenv("API_KEY")
NEXSTREAM_API_KEY = os.getenv("NEXSTREAM_API_KEY")


# =========================================================
# TMDB HELPER
# =========================================================

def get_tmdb(endpoint, params=None):

    if params is None:
        params = {}

    params["api_key"] = TMDB_API_KEY

    url = f"https://api.themoviedb.org/3/{endpoint}"

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print("TMDB Error:", response.status_code)
        return {}

    return response.json()


# =========================================================
# SEARCH API
# =========================================================

@app.route("/api/search")
def search():

    query = request.args.get("q", "").strip()

    # Don't search if query is empty
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

    for item in data.get("results", []):

        # Only movies and TV shows
        if item.get("media_type") not in ["movie", "tv"]:
            continue

        results.append({
            "id": item.get("id"),
            "media_type": item.get("media_type"),
            "title": item.get("title") or item.get("name"),
            "poster_path": item.get("poster_path"),
            "release_date": item.get("release_date") or item.get("first_air_date"),
            "overview": item.get("overview")
        })

    return {
        "results": results[:10]
    }

# =========================================================
# MOVIES PAGE
# =========================================================

@app.route("/movies")
def movies_page():

    genre = request.args.get("genre", "")
    year = request.args.get("year", "")
    rating = request.args.get("rating", "")
    sort = request.args.get("sort", "popularity.desc")
    page = request.args.get("page", 1, type=int)

    params = {
        "language": "en-US",
        "page": page,
        "sort_by": sort,
        "include_adult": False
    }

    # Genre
    if genre:
        params["with_genres"] = genre

    # Year
    if year:
        params["primary_release_year"] = year

    # Minimum rating
    if rating:
        params["vote_average.gte"] = rating

    # Make sure results have enough votes
    params["vote_count.gte"] = 50

    data = get_tmdb(
        "discover/movie",
        params
    )

    movies = data.get("results", [])

    # Get movie genres
    genre_data = get_tmdb(
        "genre/movie/list",
        {
            "language": "en-US"
        }
    )

    genres = genre_data.get("genres", [])

    return render_template(
        "movies.html",
        movies=movies,
        genres=genres,
        current_genre=genre,
        current_year=year,
        current_rating=rating,
        current_sort=sort,
        current_page=page,
        total_pages=data.get("total_pages", 1)
    )


# =========================================================
# HOME PAGE
# =========================================================

@app.route("/")
def home():

    # Popular movies
    movie_data = get_tmdb(
        "movie/popular",
        {
            "language": "en-US",
            "page": 1
        }
    )

    movies = movie_data.get("results", [])


    # Popular TV series
    tv_data = get_tmdb(
        "tv/popular",
        {
            "language": "en-US",
            "page": 1
        }
    )

    tv_shows = tv_data.get("results", [])


    return render_template(
        "index.html",
        movies=movies[:10],
        tv_shows=tv_shows[:10]
    )

# =========================================================
# MOVIE DETAIL PAGE
# =========================================================

@app.route("/movie/<int:movie_id>")
def movie_detail(movie_id):

    movie = get_tmdb(
        f"movie/{movie_id}",
        {
            "language": "en-US",
            "append_to_response": "videos"
        }
    )

    if not movie:
        return "Movie not found", 404

    # Find official trailer
    trailer = None

    videos = movie.get("videos", {}).get("results", [])

    for video in videos:

        if (
            video.get("site") == "YouTube"
            and video.get("type") == "Trailer"
            and video.get("official") is True
        ):
            trailer = video
            break

    # NexStream player
    stream_url = (
        f"https://api.codespecters.com/embed/movie/"
        f"{movie_id}?apikey={NEXSTREAM_API_KEY}"
    )

    return render_template(
        "movie.html",
        movie=movie,
        trailer=trailer,
        stream_url=stream_url
    )


# =========================================================
# TV DETAIL PAGE
# =========================================================

@app.route("/tv/<int:tv_id>")
def tv_detail(tv_id):

    show = get_tmdb(
        f"tv/{tv_id}",
        {
            "language": "en-US"
        }
    )

    if not show:
        return "TV show not found", 404

    return render_template(
        "tv.html",
        show=show,
        nexstream_api_key=NEXSTREAM_API_KEY
    )


# =========================================================
# TV SEASON EPISODES
# =========================================================

@app.route("/api/tv/<int:tv_id>/season/<int:season_number>")
def tv_season(tv_id, season_number):

    data = get_tmdb(
        f"tv/{tv_id}/season/{season_number}",
        {
            "language": "en-US"
        }
    )

    return {
        "episodes": data.get("episodes", [])
    }


# =========================================================
# TV PLAYER
# =========================================================

@app.route(
    "/tv-player/<int:tv_id>/<int:season>/<int:episode>"
)
def tv_player(tv_id, season, episode):

    stream_url = (
        f"https://api.codespecters.com/embed/tv/"
        f"{tv_id}/{season}/{episode}"
        f"?apikey={NEXSTREAM_API_KEY}"
    )

    return f"""
    <!DOCTYPE html>

    <html>

    <head>

        <style>

            html, body {{
                margin: 0;
                width: 100%;
                height: 100%;
                background: black;
            }}

            iframe {{
                width: 100%;
                height: 100%;
                border: 0;
            }}

        </style>

    </head>

    <body>

        <iframe
            src="{stream_url}"
            allowfullscreen>
        </iframe>

    </body>

    </html>
    """


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )