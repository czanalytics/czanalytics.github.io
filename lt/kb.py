from flask import Flask, request, jsonify, abort  # make_response
from flask_restful import Resource, Api
#from flask_expects_json import expects_json
from flask_cors import CORS

from datetime import datetime  # date
#import json

from db import conf, kb

app = Flask(__name__)

CORS(app)

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
       #key_check(request.headers.get('Api-Key'))

       msg = {'api': 'lane',
            'version': conf["version"],
            'endpoints': ['price', 'eta', 'co'],
            'schema_expected': conf["schema"],
            'datetime': datetime.now()
        }
        # status_code such as 200 is set automatically 
       return jsonify(msg)


class ask_kb(Resource):
    """
    KB
    """
    def get(self):
        #key_check(request.headers.get('Api-Key'))

        req = request.json
        mod = conf["model"]["price"]
        d = kb(req, mod) # !

        msg = {
            'kbs': p,
            'datetime': datetime.now()
        }
        return jsonify(msg)

    def post(self):
        req = request.json
        mod = conf["model"]["price"]
        d = kb(req, mod) # !

        msg = {
            'kb': d,
            ''datetime': datetime.now()
        }
        return jsonify(msg)



api.add_resource(intro,   '/',            endpoint='/')
api.add_resource(intro,   '/api',         endpoint='/api')

api.add_resource(ask_kb, '/api/kb',   endpoint='/api/kb')
#api.add_resource(price,   '/api/price',   endpoint='/api/price')

if __name__ == '__main__':
    app.run(conf["app_ip"], conf["app_port"])

