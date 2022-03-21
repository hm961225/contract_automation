import app


if __name__ == "__main__":
    app = app.create_app()
    app.run(host="localhost", port="9080")