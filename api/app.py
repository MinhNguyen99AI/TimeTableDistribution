from flask import Flask
from flask_restful import Api
from resources.test import Test

app = Flask(__name__)
api = Api(app)

api.add_resource(Test, '/test')
