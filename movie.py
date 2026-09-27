import requests
import os
from dotenv import load_dotenv

load_dotenv()

TMDB_API_KEY = os.getenv("API_KEY")
NEXSTREAM_API_KEY = os.getenv("NEXSTREAM_API_KEY")


# =========================================================
# GET MOVIE ID FROM USER
# =========================================================

movie_id = input("Enter TMDB movie ID: ").strip()


# =========================================================
# GET MOVIE DETAILS
# =========================================================

url = f"https://api.themoviedb.org/3/movie/{movie_id}"

params = {
    "api_key": TMDB_API_KEY,
    "language": "en-US",
    "append_to_response": "videos"
}

response = requests.get(url, params=params)


if response.status_code != 200:

    print("Movie not found.")
    exit()


movie = response.json()


# =========================================================
# MOVIE INFORMATION
# =========================================================

title = movie.get("title", "Unknown")

overview = movie.get(
    "overview",
    "No description available."
)

rating = movie.get(
    "vote_average",
    0
)

release_date = movie.get(
    "release_date",
    "N/A"
)

poster_path = movie.get(
    "poster_path"
)


if poster_path:

    poster_url = (
        "https://image.tmdb.org/t/p/w780"
        + poster_path
    )

else:

    poster_url = ""


# =========================================================
# FIND OFFICIAL YOUTUBE TRAILER
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
        video.get("site") == "YouTube"
        and video.get("type") == "Trailer"
        and video.get("official") is True
    ):

        trailer = video
        break


if trailer:

    trailer_url = (
        "https://www.youtube.com/embed/"
        + trailer["key"]
    )

else:

    trailer_url = ""


# =========================================================
# NEXSTREAM STREAM URL
# =========================================================

stream_url = (
    f"https://api.codespecters.com/embed/movie/"
    f"{movie_id}?apikey={NEXSTREAM_API_KEY}"
)


# =========================================================
# CREATE MOVIE DETAIL PAGE
# =========================================================

html = f"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>{title}</title>


<style>

* {{
    box-sizing: border-box;
}}

body {{

    margin: 0;

    background: #090909;

    color: white;

    font-family: Arial, sans-serif;

}}

.container {{

    max-width: 1200px;

    margin: auto;

    padding: 40px 20px;

}}


.back {{

    display: inline-block;

    color: #aaa;

    text-decoration: none;

    margin-bottom: 30px;

}}

.back:hover {{

    color: white;

}}


.movie-header {{

    display: grid;

    grid-template-columns: 280px 1fr;

    gap: 35px;

    margin-bottom: 40px;

}}


.poster {{

    width: 100%;

    border-radius: 10px;

}}


.movie-content h1 {{

    font-size: 40px;

    margin-top: 0;

    margin-bottom: 15px;

}}


.rating {{

    color: #ffc107;

    margin-bottom: 15px;

}}


.meta {{

    color: #999;

    margin-bottom: 25px;

}}


.overview {{

    color: #ccc;

    line-height: 1.7;

    max-width: 800px;

}}


.section-title {{

    font-size: 24px;

    margin: 40px 0 20px;

}}


.player {{

    width: 100%;

    aspect-ratio: 16 / 9;

    background: black;

    border-radius: 10px;

    overflow: hidden;

}}


.player iframe {{

    width: 100%;

    height: 100%;

    border: none;

}}


.trailer {{

    margin-top: 40px;

}}


.trailer iframe {{

    width: 100%;

    aspect-ratio: 16 / 9;

    border: none;

    border-radius: 10px;

}}


@media (max-width: 700px) {{

    .movie-header {{

        grid-template-columns: 1fr;

    }}

    .poster {{

        max-width: 280px;

    }}

    .movie-content h1 {{

        font-size: 30px;

    }}

}}

</style>

</head>


<body>


<div class="container">


<a href="movies.html" class="back">
    ← Back to Movies
</a>


<div class="movie-header">


    <div>

        <img
            class="poster"
            src="{poster_url}"
            alt="{title}"
        >

    </div>


    <div class="movie-content">

        <h1>{title}</h1>

        <div class="rating">
            ⭐ {rating:.1f} / 10
        </div>

        <div class="meta">
            Release: {release_date}
        </div>

        <p class="overview">
            {overview}
        </p>

    </div>


</div>


<h2 class="section-title">
    ▶ Watch Movie
</h2>


<div class="player">

    <iframe
        src="{stream_url}"
        allowfullscreen>
    </iframe>

</div>


"""


# =========================================================
# TRAILER
# =========================================================

if trailer:

    html += f"""

<div class="trailer">

    <h2 class="section-title">
        Official Trailer
    </h2>

    <iframe
        src="{trailer_url}"
        allowfullscreen>
    </iframe>

</div>

"""


html += """

</div>

</body>

</html>
"""


with open("movie.html", "w", encoding="utf-8") as file:

    file.write(html)


print()
print("Movie:", title)
print("TMDB ID:", movie_id)
print("NexStream URL:", stream_url)
print()
print("movie.html created successfully!")