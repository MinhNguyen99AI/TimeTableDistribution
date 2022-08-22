from flask_restful import Resource, reqparse
from resources.services import matchService
from common.constants import *
from resources.repository.mongodb import *



def excel_data_parser(data):
    if 'name' not in data or type(data['name']) != str:
        raise ValueError('name is required')

    if data['name'].split('.')[-1].lower() not in EXCEL_FILE_EXTENSIONS:
        raise ValueError('file must be excel')

    if 'data' not in data or type(data['data']) != str:
        raise ValueError('base64 data is required')

    return data


post_parser = reqparse.RequestParser()
post_parser.add_argument('schoolData', type=excel_data_parser, required=True)
post_parser.add_argument('teacherDomesticData',
                         type=excel_data_parser, required=True)
post_parser.add_argument('teacherForeignData',
                         type=excel_data_parser, required=True)


class Matcher(Resource):
    def post(self):
        args = post_parser.parse_args()
        return matchService.match(
            args['schoolData'], args['teacherDomesticData'], args['teacherForeignData'])
