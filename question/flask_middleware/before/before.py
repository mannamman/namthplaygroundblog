from flask import Flask
from api import make_api

app = Flask('App')

api = make_api()

app.register_blueprint(api, url_prefix='/test')


if __name__ == "__main__":
    app.run('127.0.0.1', '5000', debug=True)