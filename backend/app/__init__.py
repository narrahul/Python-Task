from flask import Flask
from flask_cors import CORS

from .api import register_routes
from .core import APIError, Config, db, migrate
from .core.responses import api_response


def create_app(config_object: type[Config] = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_object)

    CORS(app)
    register_extensions(app)
    register_error_handlers(app)
    register_routes(app)

    with app.app_context():
        db.create_all()

    return app


def register_extensions(app: Flask) -> None:
    db.init_app(app)
    migrate.init_app(app, db)


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(APIError)
    def handle_api_error(error: APIError):
        return api_response({"error": error.to_dict()}, status_code=error.status_code)
