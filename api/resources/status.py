from flask import Flask, request, abort
from flask_restful import Resource
from resources.services.scheduleService import getTimetableStatus
from marshmallow import Schema, fields
from common.constants import *
from resources.repository.mongodb import *


class StatusSchema(Schema):
    id = fields.Str(required=True)

status_schema = StatusSchema()

class Status(Resource):
    def get(self):
        errors = status_schema.validate(request.args)
        if errors:
            abort(400, str(errors))

        args = request.args
        return getTimetableStatus(args["id"])
