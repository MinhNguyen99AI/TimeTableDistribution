from flask_restful import Resource
from flask import send_file, request, abort
from marshmallow import Schema, fields

from resources.services.scheduleService import getTimeTableData
from common.constants import *
from resources.repository.mongodb import *

import io


class ResultSchema(Schema):
    id = fields.Str(required=True)


result_schema = ResultSchema()


class Result(Resource):

    def get(self):
        errors = result_schema.validate(request.args)
        if errors:
            abort(400, str(errors))

        args = request.args
        result_bin = getTimeTableData(args["id"])
        return send_file(
            io.BytesIO(result_bin),
            download_name="Kết quả.zip",
            mimetype='application/zip')
