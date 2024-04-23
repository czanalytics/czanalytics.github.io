from flask import Flask, request, jsonify, abort
from flask_restful import Resource, Api
from flask_cors import CORS
from datetime import datetime  # date

from lane import conf
from bundle import bundle_est, demo_est

app = Flask(__name__)

CORS(app)

api = Api(app)


def key_check(key, fk = './.key'):
    """
    Permission denied if the request header key is not correct.
    Assumes .key file.
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
    API description
    """
    def get(self):
       #key_check(request.headers.get('Api-Key'))

       msg = {'api': 'lane_bundle',
            'version': conf["version"],
            'endpoints': ['demo', 'bundle', 'demodev', 'bundledev'],
            'datetime': datetime.now()}

       return jsonify(msg)


class bundle(Resource):
    """
    Bundle transportation plant for cargo (pick, drop) -network.
    """
    def get(self):
        #key_check(request.headers.get('Api-Key'))

        req = request.json
        cnf = conf["bundle"]["routing"]
        r, doc = bundle_est(req, cnf) # !

        msg = {
            'version': conf["version"],
            'bundle_conf': cnf,
            'plan': r,
            'datetime': datetime.now(),
            'doc': doc,
            'req': req}

        return jsonify(msg)


    def post(self):
        #key_check(request.headers.get('Api-Key'))

        req = request.json
        cnf = conf["bundle"]["routing"]
        r, doc = bundle_est(req, cnf) # !

        msg = {
            'version': conf["version"],
            'bundle_conf': cnf,
            'plan': r,
            'datetime': datetime.now(),
            'doc': doc,
            'req': req}

        return jsonify(msg)


class bundledev(Resource):
    """
    Bundle transportation plant for cargo (pick, drop) -network.
    """
    def get(self):
        #key_check(request.headers.get('Api-Key'))

        req = request.json
        cnf = conf["dev"]["routing"]
        r, doc = bundle_est(req, cnf) # !

        msg = {
            'version': conf["version"],
            'bundle_conf': cnf,
            'plan': r,
            'datetime': datetime.now(),
            'doc': doc,
            'req': req}

        return jsonify(msg)


    def post(self):
        #key_check(request.headers.get('Api-Key'))

        req = request.json
        cnf = conf["dev"]["routing"]
        r, doc = bundle_est(req, cnf) # !

        msg = {
            'version': conf["version"],
            'bundle_conf': cnf,
            'plan': r,
            'datetime': datetime.now(),
            'doc': doc,
            'req': req}

        return jsonify(msg)


class demo(Resource):
    """
    Demonstrate API functionality.
    """
    def get(self):
        #key_check(request.headers.get('Api-Key'))

        req =  {"foo": "bar"}
        #req = request.json

        cnf = conf["bundle"]["demo"]
        r, doc = demo_est(req, cnf) # !

        msg = {
            'version': conf["version"],
            'demo_conf': cnf,
            'demo': r,
            'datetime': datetime.now(),
            'doc': doc,
            'req': req
        }

        return jsonify(msg)


    def post(self):
        #key_check(request.headers.get('Api-Key'))

        req = request.json
        cnf = conf["bundle"]["demo"]
        r, doc = demo_est(req, cnf) # !

        msg = {
            'version': conf["version"],
            'demo_conf': cnf,
            'demo': r,
            'datetime': datetime.now(),
            'doc': doc,
            'req': req
        }

        return jsonify(msg)


class demodev(Resource):
    """
    Demonstrate API functionality.
    """
    def get(self):
        #key_check(request.headers.get('Api-Key'))

        req =  {"foo": "bar"}
        #req = request.json

        cnf = conf["dev"]["demo"]
        r, doc = demo_est(req, cnf) # !

        msg = {
            'version': conf["version"],
            'demo_conf': cnf,
            'demo': r,
            'datetime': datetime.now(),
            'doc': doc,
            'req': req
        }

        return jsonify(msg)


    def post(self):
        #key_check(request.headers.get('Api-Key'))

        req = request.json
        cnf = conf["dev"]["demo"]
        r, doc = demo_est(req, cnf) # !

        msg = {
            'version': conf["version"],
            'demo_conf': cnf,
            'demo': r,
            'datetime': datetime.now(),
            'doc': doc,
            'req': req
        }

        return jsonify(msg)

api.add_resource(intro,  '/',           endpoint='/')
api.add_resource(intro,  '/api',        endpoint='/api')

api.add_resource(bundle, '/api/bundle', endpoint='/api/bundle')
api.add_resource(demo,   '/api/demo',   endpoint='/api/demo')

api.add_resource(bundledev, '/api/bundledev', endpoint='/api/bundledev')
api.add_resource(demodev,   '/api/demodev',   endpoint='/api/demodev')

if __name__ == '__main__':
    app.run(conf["app_ip"], conf["bundle_port"])

