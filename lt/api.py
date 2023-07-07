from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api
from flask_expects_json import expects_json

from datetime import datetime, date
import json

from lane import conf
from lane import price_est, eta_est, co_est, route_est

app = Flask(__name__)

api = Api(app)

class intro(Resource):
    """
    api description
    """
    def get(self):
       # req = request.json

        msg = {
            'api': 'lane',
            'version': conf["version"],
            'endpoints': ['price', 'eta', 'co'],
            'schema_expected': conf["schema"],
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
        mod = conf["model"]["price"]
        p, p_lo, p_hi, meta = price_est(req, mod) # !

        msg = {
            'price': p, 'price_lo': p_lo, 'price_hi': p_hi,
            'model': mod,
            'datetime': datetime.now(),
            'meta': meta,
            'req': req
        }
        return jsonify(msg)

    def post(self):
        msg = {'x': 1}
        return jsonify(msg)

class eta(Resource):
    """
    Lane ETA estimate
    """
    def get(self):
        req = request.json
        mod = conf["model"]["eta"]
        t, t_lo, t_hi, meta = eta_est(req, mod) # !

        msg = {
            'eta': t, 'eta_lo': t_lo, 'eta_hi': t_hi,
            'model': mod,
            'datetime': datetime.now(),
            'meta': meta,
            'req': req
        }
        return jsonify(msg)

class co(Resource):
    """
    Lane CO2 estimate
    """
    def get(self):
        req = request.json
        mod = conf["model"]["co"]
        co, co_lo, co_hi, meta = co_est(req, mod) # !

        msg = {
            'co': co, 'co_lo': co_lo, 'co_hi': co_hi,
            'model': mod,
            'datetime': datetime.now(),
            'meta': meta,
            'req': req
        }
        return jsonify(msg)

class route(Resource):
    """
    Route estimated
    """
    def get(self):
        req = request.json
        cnf = conf["routing"]
        route = route_est(req, cnf) # !

        msg = {
            'route': route,
            'routing': cnf,
            'datetime': datetime.now(),
            'req': req
        }
        return jsonify(msg)

api.add_resource(intro, '/',          endpoint='/')
api.add_resource(intro, '/api',       endpoint='/api')

api.add_resource(price, '/api/price', endpoint='/api/price')
api.add_resource(eta,   '/api/eta',   endpoint='/api/eta')
api.add_resource(co,    '/api/co',    endpoint='/api/co')
api.add_resource(route, '/api/route', endpoint='/api/route')

if __name__ == '__main__':
    app.run(conf["app_ip"], conf["app_port"])

