from flask import Flask
from flask_restful import Api
app = Flask(__name__)
api = Api(app)
from application import routesApi
from application import routes
from datetime import timedelta
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)

