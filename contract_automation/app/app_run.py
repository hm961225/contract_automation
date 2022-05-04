import app
from flask_cors import CORS


if __name__ == "__main__":
    app = app.create_app()
    CORS(app, supports_credentials=True)
    app.run(host="localhost", port="9080")