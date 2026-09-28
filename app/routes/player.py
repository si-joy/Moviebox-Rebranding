from flask import (
    Blueprint,
    render_template,
    request
)

player_bp = Blueprint(
    "player",
    __name__
)

SERVERS = {
    "vidsrc_to": {
        "name": "VidSrc.to (Default)",
        "movie": "https://vidsrc.to/embed/movie/{id}",
        "tv": "https://vidsrc.to/embed/tv/{id}/{season}/{episode}"
    },
    "smashystream": {
        "name": "SmashyStream (⚡ Multi-Source & Ultra Fast)",
        "movie": "https://embed.smashystream.com/playere.php?tmdb={id}",
        "tv": "https://embed.smashystream.com/playere.php?tmdb={id}&season={season}&episode={episode}"
    },
    "embedsu": {
        "name": "EmbedSu (🛡️ AdBlock Safe & Fast)",
        "movie": "https://embed.su/embed/movie/{id}",
        "tv": "https://embed.su/embed/tv/{id}/{season}/{episode}"
    },
    "rive": {
        "name": "Rive Stream (🚀 Low Latency)",
        "movie": "https://rivestream.xyz/embed/movie/{id}",
        "tv": "https://rivestream.xyz/embed/tv/{id}/{season}/{episode}"
    },
    "vidsrc_icu": {
        "name": "VidSrc ICU (⚡ Fast Load)",
        "movie": "https://vidsrc.icu/embed/movie/{id}",
        "tv": "https://vidsrc.icu/embed/tv/{id}/{season}/{episode}"
    },
    "vidlink": {
        "name": "VidLink (🌟 Clean UI)",
        "movie": "https://vidlink.pro/movie/{id}",
        "tv": "https://vidlink.pro/tv/{id}/{season}/{episode}"
    },
    "autoembed": {
        "name": "AutoEmbed (🚀 CDN Powered)",
        "movie": "https://player.autoembed.cc/embed/movie/{id}",
        "tv": "https://player.autoembed.cc/embed/tv/{id}/{season}/{episode}"
    },
    "multiembed": {
        "name": "SuperEmbed (🎯 Direct Stream)",
        "movie": "https://multiembed.mov/directstream.php?video_id={id}&tmdb=1",
        "tv": "https://multiembed.mov/directstream.php?video_id={id}&tmdb=1&s={season}&e={episode}"
    },
    "vidsrc_me": {
        "name": "VidSrc.me (📌 Classic Stable)",
        "movie": "https://vidsrc.me/embed/movie/{id}",
        "tv": "https://vidsrc.me/embed/tv/{id}/{season}/{episode}"
    },
    "2embed": {
        "name": "2Embed",
        "movie": "https://www.2embed.cc/embed/{id}",
        "tv": "https://www.2embed.cc/embedtv/{id}&s={season}&e={episode}"
    },
    "vidsrc_dev": {
        "name": "VidSrc.vip / Dev (⚡ Best for TV Shows)",
        "movie": "https://vidsrc.vip/embed/movie/{id}",
        "tv": "https://vidsrc.vip/embed/tv/{id}/{season}/{episode}"
    },
    "vidsrc_cc": {
        "name": "VidSrc.cc (🚀 Working Fast Server)",
        "movie": "https://vidsrc.cc/v2/embed/movie/{id}",
        "tv": "https://vidsrc.cc/v2/embed/tv/{id}/{season}/{episode}"
    },
    "vidsrc_in": {
        "name": "VidSrc.in (🎯 Alternate TV Stream)",
        "movie": "https://vidsrc.in/embed/movie/{id}",
        "tv": "https://vidsrc.in/embed/tv/{id}/{season}/{episode}"
    },
    "vidsrc_to": {
        "name": "VidSrc.to",
        "movie": "https://vidsrc.to/embed/movie/{id}",
        "tv": "https://vidsrc.to/embed/tv/{id}/{season}/{episode}"
    },
    "smashystream": {
        "name": "SmashyStream",
        "movie": "https://embed.smashystream.com/playere.php?tmdb={id}",
        "tv": "https://embed.smashystream.com/playere.php?tmdb={id}&season={season}&episode={episode}"
    },
    "embedsu": {
        "name": "EmbedSu",
        "movie": "https://embed.su/embed/movie/{id}",
        "tv": "https://embed.su/embed/tv/{id}/{season}/{episode}"
    }
}

@player_bp.route("/movie-player/<int:movie_id>")
def movie_player(movie_id):
    # Default set to 'vidsrc_to'
    server_key = request.args.get("server", "vidsrc_to")
    selected_server = SERVERS.get(server_key, SERVERS["vidsrc_to"])
    
    stream_url = selected_server["movie"].format(id=movie_id)

    return render_template(
        "pages/player.html",
        stream_url=stream_url,
        content_id=movie_id,
        content_type="movie",
        servers=SERVERS,
        current_server=server_key
    )

@player_bp.route("/tv-player/<int:tv_id>/<int:season>/<int:episode>")
def tv_player(tv_id, season, episode):
    # Default set to 'vidsrc_to'
    server_key = request.args.get("server", "vidsrc_to")
    selected_server = SERVERS.get(server_key, SERVERS["vidsrc_to"])
    
    stream_url = selected_server["tv"].format(
        id=tv_id,
        season=season,
        episode=episode
    )

    return render_template(
        "pages/player.html",
        stream_url=stream_url,
        content_id=tv_id,
        season=season,
        episode=episode,
        content_type="tv",
        servers=SERVERS,
        current_server=server_key
    )