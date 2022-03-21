from flask import Flask
from app import routes
from config import Config


def create_app():
    app = Flask(__name__)
    routes.init_route(app)
    app.config.from_object(Config)
    return app
