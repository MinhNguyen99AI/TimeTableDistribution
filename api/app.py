from flask import Flask
from flask_restful import Api
from resources.matcher import Matcher

app = Flask(__name__)
api = Api(app)

api.add_resource(Matcher, '/match')
