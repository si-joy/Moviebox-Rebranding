import os

from flask import Flask, app
from dotenv import load_dotenv


def create_app():
    load_dotenv()

    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )

    app.config["TMDB_API_KEY"] = os.getenv("TMDB_API_KEY")
    app.config["NEXSTREAM_API_KEY"] = os.getenv("NEXSTREAM_API_KEY")

    from app.routes.home import home_bp
    from app.routes.movies import movies_bp
    from app.routes.tv import tv_bp
    from app.routes.search import search_bp
    from app.routes.player import player_bp
    from app.routes.midnight import midnight_bp



    app.register_blueprint(home_bp)
    app.register_blueprint(movies_bp)
    app.register_blueprint(tv_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(player_bp)
    app.register_blueprint(midnight_bp)

    return app