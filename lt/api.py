from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api
from flask_expects_json import expects_json

from datetime import datetime, date
import json

# https://apiflask.com/api/app/
# https://github.com/Fischerfredl/flask-expects-json
# https://lovelace.oulu.fi/ohjelmoitava-web/programmable-web-project-spring-2019/implementing-rest-apis-with-flask/
# pip install jsonschema ?
# curl https://stackoverflow.com/questions/52133268/flask-get-requests-with-json-parameter-using-curl
# https://stackoverflow.com/questions/13081532/return-json-response-from-flask-view

app = Flask(__name__)

api = Api(app)

class api_greet(Resource):
    def get(self):
        return 'API v0.26'

price_schema =  {'type': 'object',
                 'properties': {
                     'mode': {'type': 'string'},
                     'distance': {'type': 'string'}},
                 'required': ['mode']
                 }


#@app.route('/api/bar', methods=['GET', 'POST'])
#@expects_json(price_schema)
#def bar():
#    return 'bar'

#@app.route('/api/foo', methods=['GET', 'POST'])

def price_est(d, price_km=2, price_min=100, err=0.1):
    """
    Simplistic transportation price estimate
    price, p [EUR] =  straight_line(distance, d [km], price/km [EUR/km], price_min [EUR])
    """
    p = price_km * d + price_min
    p_lo = p - p * err
    p_hi = p + p * err

    return p, p_lo, p_hi

def eta_est(d, v=100, err=0.1):
    """
    Simplistic transportation time estimate
    time, t [h] = distance, d [km] / speed, v [km/h]
    """
    t = d / v
    t_lo = t - t * err
    t_hi = t + t * err
    return t, t_lo, t_hi

def co_est(d, c=100, err=0.2):
    """
    Simplistic transportation CO2 exhaust estimate
    CO2 [g] =  distance, d [km] * CO2, c [g/km]
    """
    co = d * c
    co_lo = co - co * err
    co_hi = co + co * err
    return co, co_lo, co_hi

class price(Resource):
    def get(self):
        req = request.json
        dist = req['distance']

        p, p_lo, p_hi = price_est(dist) # !

        d = {'left': 0.17037454,
             'right': 0.82339555,
             '_unknown_': 0.0059609693
             }

        message = {
            'price': p,
            'price_lo': p_lo,
            'price_hi': p_hi,
            'datetime': datetime.now(),
            'req': req
        }

        resp = jsonify(message)
        resp.status_code = 200

        print(resp)
        return resp
        #return jsonify(d) 

    def post(self):
        return jsonify(
            greeting=["foo", "post"],
            date=datetime.today(),
        )
        #return 'POST'

class eta(Resource):
    def get(self):
        req = request.json
        d = req['distance']

        t, t_lo, t_hi = eta_est(d) # !

        message = {
            'eta': t,
            'eta_lo': t_lo,
            'eta_hi': t_hi,
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
        d = req['distance']

        co, co_lo, co_hi = co_est(d) # !

        message = {
            'co': co,
            'co_lo': co_lo,
            'co_hi': co_hi,
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

def foo2():
  if request.method=='GET':
     json_arg = json.loads(request.args.get("json_arg", None))
     non_json_arg = request.args.get("non_json_arg", None)
     return "json arg: %s non_json_arg: %s"%(json_arg, non_json_arg)
     #return 'GET'
  elif request.method=='POST':
     return 'POST'
  else:
     return 'ok'

#   if request.is_json:
#      data = request.json
#      print(data.get('mode'))
#      print(data.get('distance'))
#      return data
#   else:
#      return make_response(jsonify({'distance': 1000}), 200)

"""
class price(Resource):
    def get(self):
        #return 'Price'
        return make_response(jsonify({'price': 9.99}), 200)

    def post(self):
        pass

class eta(Resource):
    def get(self):
        return jsonify(id=1111, mode="truck", distance=1000, eta=12.3)

    def post(self):
        pass

class co(Resource):
    def get(self):
        return jsonify(id=1111, mode="truck", distance=1000, co2=666)

    def post(self):
        pass
"""

api.add_resource(api_greet, '/', endpoint='/') # Route_1

api.add_resource(api_greet, '/api', endpoint='/api') #

api.add_resource(price, '/api/price', endpoint='/api/price')
api.add_resource(eta,   '/api/eta',   endpoint='/api/eta')
api.add_resource(co,    '/api/co',    endpoint='/api/co')

if __name__ == '__main__':
    app.run('0.0.0.0', '3333')

