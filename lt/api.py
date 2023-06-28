from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api
from flask_expects_json import expects_json

from datetime import datetime, date
import json

from lane import price_est, eta_est, co_est

app = Flask(__name__)

api = Api(app)

schema =  {'type': 'object',
                 'properties': {
                     'date': {'type': 'string'},
                     'from_lat': {'type': 'float'}},
                 'required': ['date', 'from_lat']
           }

class intro(Resource):
    """
    api description
    """
    def get(self):
       # req = request.json

        msg = {
            'api': 'lane_calculator',
            'version': 0.27,
            'endpoints': ['price', 'eta', 'co'],
            'schema_expected': schema,
            'datetime': datetime.now()
        }
        # status_code such as 200 is set automatically 
        return jsonify(msg)

class price(Resource):
    """
    Lane price estimate
    """
    def get(self):
        req = request.json
        p, p_lo, p_hi = price_est(req) # !

        msg = {
            'price': p, 'price_lo': p_lo, 'price_hi': p_hi,
            'datetime': datetime.now(),
            'req': req
        }
        return jsonify(msg)

    def post(self):
        return jsonify(
            greeting = ["foo", "post"],
            date = datetime.today(),
        )

class eta(Resource):
    """
    Lane ETA estimate
    """
    def get(self):
        req = request.json
        t, t_lo, t_hi = eta_est(req) # !

        msg = {
            'eta': t, 'eta_lo': t_lo, 'eta_hi': t_hi,
            'datetime': datetime.now(),
            'req': req
        }
        return jsonify(msg)

    def post(self):
        return jsonify(
            greeting = ["foo", "post"],
            date = datetime.today(),
        )

class co(Resource):
    """
    Lane CO2 estimate
    """
    def get(self):
        req = request.json
        co, co_lo, co_hi = co_est(req) # !

        msg = {
            'co': co, 'co_lo': co_lo, 'co_hi': co_hi,
            'datetime': datetime.now(),
            'req': req
        }
        return jsonify(msg)

    def post(self):
        return jsonify(
            greeting = ["foo", "post"],
            date = datetime.today(),
        )

api.add_resource(intro, '/',          endpoint='/')
api.add_resource(intro, '/api',       endpoint='/api')

api.add_resource(price, '/api/price', endpoint='/api/price')
api.add_resource(eta,   '/api/eta',   endpoint='/api/eta')
api.add_resource(co,    '/api/co',    endpoint='/api/co')

if __name__ == '__main__':
    app.run('0.0.0.0', '3333')

