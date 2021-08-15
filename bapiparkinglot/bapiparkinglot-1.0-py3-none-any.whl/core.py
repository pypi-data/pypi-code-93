from flask import Flask, Blueprint
from flask_restful import reqparse, Api, Resource
from bapiparkinglot.model.model_parking_lot import ParkingLot

__author__ = 'Haryo Bagas Assyafah'
__copyright__ = 'Copyright 2021 Bear Au Jus - ジュースとくま'
__credits__ = ['Haryo Bagas Assyafah']
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Haryo Bagas Assyafah"
__email__ = "haryobagasasyafah6@gmail.com"
__status__ = "Production"

app = Flask(__name__)
api = Api(app)
api_bp = Blueprint('api', __name__)
app.register_blueprint(api_bp)

model = {}
auth = 'C3E7A714E3C268BEC0448EFDDD9E040F68EB0879402DA413C72A2FB49DD45F65'


class Parkinglot(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('auth', type=str, help='required', required=True)
        args = parser.parse_args()

        if not args['auth'] == auth:
            return {'messages': 'invalid auth'}, 401

        return {'list_registered_parking_lot': {int(i): model[i].total_slots for i in model.keys()}}, 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('auth', type=str, help='required', required=True)
        parser.add_argument('total_slots', type=int,
                            help='required', required=True)
        args = parser.parse_args()

        if not args['auth'] == auth:
            return {'messages': 'invalid auth'}, 401

        if args['total_slots'] < 1:
            return {'messages': 'total_slots must be >= 1'}, 400

        if model:
            id_parking_lot = int(max(model.keys())) + 1
        else:
            id_parking_lot = 0

        model[id_parking_lot] = ParkingLot(args['total_slots'])
        return {'parking_lot_id': id_parking_lot, 'total_slots': model[id_parking_lot].total_slots, 'messages': 'new parking lot succesfully created'}, 201


class ParkinglotSlots(Resource):
    def get(self, id_parking_lot):
        parser = reqparse.RequestParser()
        parser.add_argument('auth', type=str, help='required', required=True)
        parser.add_argument('view', type=int)
        args = parser.parse_args()

        if not args['auth'] == auth:
            return {'messages': 'invalid auth'}, 401

        if id_parking_lot in model:
            if args['view'] or args['view'] == 0:
                # get data parking lot slots by number plate
                if args['view'] == 1:
                    parser.add_argument(
                        'number_plate', type=str, help='required', required=True)
                    args = parser.parse_args()
                    output = model[id_parking_lot].info_car(
                        args['number_plate'])
                    return output[1], output[0]

                # get data parking lot slots by color
                elif args['view'] == 2:
                    parser.add_argument('color', type=str,
                                        help='required', required=True)
                    args = parser.parse_args()
                    output = model[id_parking_lot].info_slots(args['color'])
                    return output[1], output[0]

                # get data list car info by color
                elif args['view'] == 3:
                    parser.add_argument('color', type=str,
                                        help='required', required=True)
                    args = parser.parse_args()
                    output = model[id_parking_lot].info_color(args['color'])
                    args = parser.parse_args()
                    return output[1], output[0]

                return {'messages': 'invalid view index'}, 404
            return {'parking_lot_id': id_parking_lot, 'data': model[id_parking_lot].data()}, 200
        return {'messages': f'parking_lot_id={id_parking_lot} not found'}, 404

    def post(self, id_parking_lot):
        parser = reqparse.RequestParser()
        parser.add_argument('auth', type=str, help='required', required=True)
        parser.add_argument('number_plate', type=str,
                            help='required', required=True)
        parser.add_argument('color', type=str, help='required', required=True)
        args = parser.parse_args()

        if not args['auth'] == auth:
            return {'messages': 'invalid auth'}, 401

        if id_parking_lot in model:
            res = model[id_parking_lot].park(
                args['number_plate'], args['color'])
            return res[1], res[0]
        else:
            return {'messages': f'parking_lot_id={id_parking_lot} not found'}, 404

    def put(self, id_parking_lot):
        parser = reqparse.RequestParser()
        parser.add_argument('auth', type=str, help='required', required=True)
        parser.add_argument('number_plate', type=str,
                            help='required', required=True)
        args = parser.parse_args()

        if not args['auth'] == auth:
            return {'messages': 'invalid auth'}, 401

        if id_parking_lot in model:
            res = model[id_parking_lot].unpark(args['number_plate'])
            return res[1], res[0]
        else:
            return {'messages': f'parking_lot_id={id_parking_lot} not found'}, 404


api.add_resource(Parkinglot, '/parking-lot')
api.add_resource(ParkinglotSlots, '/parking-lot/<int:id_parking_lot>')


def run():
    print(" ----------------------------------------------------")
    print(" * Application 'Parking Lot API'")
    print(" * Author 'Haryo Bagas Assyafah'")
    print(" * Default Auth Token 'C3E7A714E3C268BEC0448EFDDD9E040F68EB0879402DA413C72A2FB49DD45F65'")
    print(" ----------------------------------------------------")
    app.run(host='0.0.0.0', port=25565)
