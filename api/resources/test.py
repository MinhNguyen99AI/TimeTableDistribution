from flask_restful import Resource, fields, marshal_with
from flask import request


resource_fields = {
	'id': fields.Integer,
	'name': fields.String,
	'views': fields.Integer,
	'likes': fields.Integer
}

class Test(Resource):
    def get(self):

        return "Hello"

    @marshal_with(resource_fields)
    def post(self):
        return request.json
