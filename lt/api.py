from flask import Flask, request, jsonify, abort  # make_response
from flask_restful import Resource, Api
#from flask_expects_json import expects_json

from datetime import datetime  # date
#import json

from lane import conf
from lane import price_est, eta_est, co_est, route_est, config_lane, status_lane, report_lane

app = Flask(__name__)

api = Api(app)


def key_check(key, fk = './.key'):
    """
    Permission denied if the request header key is not correct
    """
    with open(fk) as f:
        k = f.read()

    secret_key = k.replace('\n', '')

    if key == secret_key:
        key_ok = True
    else:
        key_ok = False

    #key_ok = True   # testing
    #key_ok = False

    if not key_ok:
        abort(403) # permission denied

    return 1


class intro(Resource):
    """
    api description
    """
    def get(self):
       key_check(request.headers.get('Api-Key'))

       msg = {'api': 'lane',
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
        key_check(request.headers.get('Api-Key'))

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
        key_check(request.headers.get('Api-Key'))

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
        key_check(request.headers.get('Api-Key'))

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
        key_check(request.headers.get('Api-Key'))

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


class config(Resource):
    """
    Service configuration
    """
    def get(self):
        key_check(request.headers.get('Api-Key'), fk = './.key_conf')

        req = request.json
        cnf = conf["config"]
        r = config_lane(req, cnf) # !
        msg = {
            'config': r,
            'datetime': datetime.now(),
            'req': req
        }
        return jsonify(msg)


class status(Resource):
    """
    Service status
    """
    def get(self):
        key_check(request.headers.get('Api-Key'))

        req = request.json
        cnf = conf["status"]
        r = status_lane(req, cnf) # !

        msg = {
            'status': r,
            'datetime': datetime.now(),
            'req': req
        }
        return jsonify(msg)


class report(Resource):
    """
    Create report
    """
    def get(self):
        key_check(request.headers.get('Api-Key'))

        req = request.json
        cnf = conf["report"]
        r = report_lane(req, cnf) # !

        msg = {
            'report': r,
            'datetime': datetime.now(),
            'req': req
        }
        return jsonify(msg)


api.add_resource(intro, '/',            endpoint='/')
api.add_resource(intro, '/api',         endpoint='/api')

api.add_resource(price, '/api/price',   endpoint='/api/price')
api.add_resource(eta,   '/api/eta',     endpoint='/api/eta')
api.add_resource(co,    '/api/co',      endpoint='/api/co')
api.add_resource(route, '/api/route',   endpoint='/api/route')

api.add_resource(config, '/api/config', endpoint='/api/config')
api.add_resource(status, '/api/status', endpoint='/api/status')
api.add_resource(report, '/api/report', endpoint='/api/report')

if __name__ == '__main__':
    app.run(conf["app_ip"], conf["app_port"])

