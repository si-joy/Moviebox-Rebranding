from flask import Blueprint, render_template

live_bp = Blueprint("live", __name__)


@live_bp.route("/live")
def live_page():
    channels = [
        {
            "name": "Star Jalsha",
            "logo": "https://static.wikia.nocookie.net/logopedia/images/7/7a/Star_Jalsha_2016.png",
            "embed_url": "https://www.yupptv.com/channels/star-jalsha/live/embed"
        }
    ]

    return render_template(
        "pages/live.html",
        channels=channels
    )