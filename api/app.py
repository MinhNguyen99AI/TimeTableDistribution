from flask import Flask
from flask_restful import Api
from resources.matcher import Matcher
from resources.result import Result
from resources.status import Status
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

api.add_resource(Matcher, '/match')
api.add_resource(Result, '/result')
api.add_resource(Status, '/status')

if __name__ == "__main__":
    app.run(debug=True)
