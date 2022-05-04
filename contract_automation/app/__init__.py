from flask import Flask
from app import routes
from config import Config
from app import models


def create_app():
    app = Flask(__name__)
    routes.init_route(app)
    models.init_db()
    app.config.from_object(Config)
    return app
