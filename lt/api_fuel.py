from flask import Flask, request, jsonify, abort  # make_response
from flask_restful import Resource, Api
#from flask_expects_json import expects_json
from flask_cors import CORS

from datetime import datetime  # date
#import json

from lane import conf
from lane import fuel_est

app = Flask(__name__)

CORS(app)

api = Api(app)


class intro(Resource):
    """
    api description
    """
    def get(self):

       msg = {'api': 'lane_fuel',
            'version': conf["version"],
            'endpoints': ['fuel'],
            'datetime': datetime.now()
        }
       return jsonify(msg)


class fuel(Resource):
    """
    Fuel price info.
    """
    def get(self):

        req = request.json
        cnf = conf["fuel"]["price"]
        r, doc = fuel_est(req, cnf) # !

        msg = {
            'version': conf["version"],
            'fuel_conf': cnf,
            'fuel_price': r,
            'datetime': datetime.now(),
            'doc': doc,
            'req': req
        }
        return jsonify(msg)


    def post(self):

        req = request.json
        cnf = conf["fuel"]["price"]
        r, doc = fuel_est(req, cnf) # !

        msg = {
            'version': conf["version"],
            'fuel_conf': cnf,
            'fuel_price': r,
            'datetime': datetime.now(),
            'doc': doc,
            'req': req
        }
        return jsonify(msg)


class tc(Resource):
    ### @app.route('your route', methods=['GET'])

    def get(self):
        response = jsonify({'some': 'data'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


api.add_resource(intro,   '/',            endpoint='/')
api.add_resource(intro,   '/api',         endpoint='/api')

api.add_resource(fuel, '/api/fuel', endpoint='/api/fuel') # fuel API

#api.add_resource(tc,'/api/tc',   endpoint='/api/tc')

if __name__ == '__main__':
    app.run(conf["app_ip"], conf["fuel_port"])

