from flask import Flask
from flask_restful import Api
from resources.matcher import Matcher
from flask_cors import CORS

app = Flask(__name__)
api = Api(app)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

api.add_resource(Matcher, '/match')

if __name__ == "__main__":
    app.run(debug=True)
