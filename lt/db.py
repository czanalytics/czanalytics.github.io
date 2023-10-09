# db.py implement kb.py endpoints
#

import logging as log # log.debug/info/warning 
import json
import pandas as pd
import datetime
import net


conf_schema = {'type': 'object', 'properties': {
    'id':   {'type': 'string'},
    'seg':  {'type': 'integer'}, # voyage segment 1,2, ...
    'co':   {'type': 'integer'}, # co2 g/km 
    'da':   {'type': 'string'},  # date, time [a, b] -range
    'ta':   {'type': 'string'},
    'db':   {'type': 'string'},
    'tb':   {'type': 'string'},
    'lat1': {'type': 'float'},   # latitude, longitude [1, 2] from, to - coordinates 
    'lon1': {'type': 'float'},   # format D.ddddd with 5 decimals has ~1 m accuracy
    'lat2': {'type': 'float'},
    'lon2': {'type': 'float'}},
    'required': ['id', 'seg', 'co', 'da', 'lat1', 'lon1', 'lat2', 'lon2']
          }

conf_data = {'data', 'foo'}

# model conf simple/lite/gam/autom
conf_model = {'price': 'price_lite', 'eta': 'eta_lite','co': 'co_simple'}      # lite

# route conf
conf_route = {'service': 'route_streetmap', 'foo': 'bar'}

# routing conf
conf_routing = {'service': 'routing_consolidate', 'foo': 'bar'}

# management confs
conf_config = {'config': 'foo'} # manage (multiple)config files, pricing
conf_status = {'status': 'foo'}
conf_report = {'report': 'foo'}

conf = {'version':  0.40,
        'app_ip':   '0.0.0.0',
        'app_port': 3333,
        'schema':   conf_schema,
        'data':     conf_data,
        'model':    conf_model,
        'route':    conf_route,
        'routing':  conf_routing,
        'config':   conf_config,
        'status':   conf_status,
        'report':   conf_report
        }


lv = log.DEBUG
log.basicConfig(format='%(asctime)s, %(name)s, %(levelname)s: %(message)s, %(funcName)s:%(lineno)s', level=lv)

#dp = pd.read_csv("./nuts.csv") # data for lite-models

#log.INFO('data read')

def get_conf():
 with open('./kb.yml', 'r') as JSON:
       dic = json.load(JSON)
 return dic

#con = get_conf()

def kb(d, mod):
    """
    KB  EVAL
    """

    d = 0

    return d

