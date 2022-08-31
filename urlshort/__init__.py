from . import urlshort
from flask import Flask

def create_app(test_config=None):
    app = Flask(__name__)
    # secret_key needed to pass messages around, like when using flash
    app.secret_key = '123abc456efg789hik'

    app.register_blueprint(urlshort.bp)

    return app
