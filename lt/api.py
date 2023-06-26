from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api
from flask_expects_json import expects_json

from datetime import datetime, date
import json

#import lane
from lane import price_est, eta_est, co_est

# https://apiflask.com/api/app/
# https://github.com/Fischerfredl/flask-expects-json
# https://lovelace.oulu.fi/ohjelmoitava-web/programmable-web-project-spring-2019/implementing-rest-apis-with-flask/
# pip install jsonschema ?
# curl https://stackoverflow.com/questions/52133268/flask-get-requests-with-json-parameter-using-curl
# https://stackoverflow.com/questions/13081532/return-json-response-from-flask-view

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

        message = {
            'api': 'lane_calculator',
            'version': 0.26,
            'endpoints': ['price', 'eta', 'co'],
            'schema_expected': schema,
            'datetime': datetime.now(),
        }

        resp = jsonify(message)
        resp.status_code = 200

        print(resp)
        return resp

class price(Resource):
    def get(self):
        req = request.json
        p, p_lo, p_hi = price_est(req) # !

        message = {
            'price': p, 'price_lo': p_lo, 'price_hi': p_hi,
            'datetime': datetime.now(),
            'req': req
        }

        resp = jsonify(message)
        resp.status_code = 200

        print(resp)
        return resp

    def post(self):
        return jsonify(
            greeting=["foo", "post"],
            date=datetime.today(),
        )

class eta(Resource):
    def get(self):
        req = request.json
        t, t_lo, t_hi = eta_est(req) # !

        message = {
            'eta': t, 'eta_lo': t_lo, 'eta_hi': t_hi,
            'datetime': datetime.now(),
            'req': req
        }

        resp = jsonify(message)
        resp.status_code = 200

        print(resp)
        return resp

    def post(self):
        return jsonify(
            greeting=["foo", "post"],
            date=datetime.today(),
        )

class co(Resource):
    def get(self):
        req = request.json
        co, co_lo, co_hi = co_est(req) # !

        message = {
            'co': co, 'co_lo': co_lo, 'co_hi': co_hi,
            'datetime': datetime.now(),
            'req': req
        }

        resp = jsonify(message)
        resp.status_code = 200

        print(resp)
        return resp

    def post(self):
        return jsonify(
            greeting=["foo", "post"],
            date=datetime.today(),
        )

api.add_resource(intro, '/', endpoint='/') #
api.add_resource(intro, '/api', endpoint='/api') #

api.add_resource(price, '/api/price', endpoint='/api/price')
api.add_resource(eta,   '/api/eta',   endpoint='/api/eta')
api.add_resource(co,    '/api/co',    endpoint='/api/co')

if __name__ == '__main__':
    app.run('0.0.0.0', '3333')

