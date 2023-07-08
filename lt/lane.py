# lane.py
# functions for api.py endpoints
#
# https://apiflask.com/api/app/
# https://github.com/Fischerfredl/flask-expects-json
# https://lovelace.oulu.fi/ohjelmoitava-web/programmable-web-project-spring-2019/implementing-rest-apis-with-flask/
# curl https://stackoverflow.com/questions/52133268/flask-get-requests-with-json-parameter-using-curl
# https://stackoverflow.com/questions/13081532/return-json-response-from-flask-view
# https://www.toptal.com/python/in-depth-python-logging

import logging as log # log.debug/info/warning 
#import json
#import numpy as np
import pandas as pd
#from geopy.distance import geodesic

schema_api = {'type': 'object', 'properties': {
    'id': {'type': 'string'},
    'seg': {'type': 'integer'}, # voyage segment 1,2, ...
    'co': {'type': 'integer'},  # co2 g/km 
    'da': {'type': 'string'},   # date, time [a, b] -range
    'ta': {'type': 'string'},
    'db': {'type': 'string'},
    'tb': {'type': 'string'},
    'lat1': {'type': 'float'},  # latitude, longitude [1, 2] from, to - coordinates 
    'lon1': {'type': 'float'},  # format D.ddddd with 5 decimals has ~1 m accuracy
    'lat2': {'type': 'float'},
    'lon2': {'type': 'float'}},
    'required': ['id', 'seg', 'co', 'da', 'lat1', 'lon1', 'lat2', 'lon2']
          }

mods = {'price': 'price_lite', 'eta': 'eta_simple','co': 'co_simple' }
#mods = {'price': 'price_simple', 'eta': 'eta_simple','co': 'co_simple' }
#mods = {'price': 'price_lite', 'eta': 'eta_lite','co': 'co_lite' }
#mods = {'price': 'price_gam', 'eta': 'eta_gam','co': 'co_gam' }
#mods = {'price': 'price_automl', 'eta': 'eta_automl','co': 'co_automl' }

routing = {'service': 'route_streetmap', 'foo': 'bar'}
#routing = {'service': 'route_openroute'}
#routing = {'service': 'route_googlemaps'}

conf = {'version': 0.27,
        'app_ip': '0.0.0.0',
        'app_port': 3333,
        'schema': schema_api,
        'model': mods,
        'routing': routing
        }

lv = log.DEBUG
#l = log.ERROR
log.basicConfig(format='%(asctime)s, %(name)s, %(levelname)s, \
                %(funcName)s:%(lineno)s, %(message)s', level=lv)
#log.basicConfig(format='%(asctime)s, %(levelname)s, %(message)s', level=lv)

dp = pd.read_csv("./nuts.csv")
dd = pd.read_csv("./nuts_centroid.csv")

#log.INFO('data read')

def price_est(d, mod):
    """
    Dispatch price calculation to requested model
    """
    match mod:
        case 'price_simple':
            p, p_lo, p_hi, meta = price_simple(d)
        case 'price_lite':
            p, p_lo, p_hi, meta = price_lite(d)
        case 'price_gam':
            p, p_lo, p_hi, meta = 0, 0, 0, 0
            #p, p_lo, p_hi, meta = price_gam(d)
        case 'price_automl':
            p, p_lo, p_hi, meta = 0, 0, 0, 0
            #p, p_lo, p_hi, meta = price_automl(d)
        case _:
            p, p_lo, p_hi, meta = 0, 0, 0, 0
            #log.ERROR('unknown model') # fails

    return round(p), round(p_lo), round(p_hi), meta


def eta_est(d, mod):
    """
    Dispatch ETA calculation to requested model
    """
    # structural pattern mathing, https://peps.python.org/pep-0622/
    match mod:
        case 'eta_simple':
            t, t_lo, t_hi, meta = eta_simple(d)
        case 'eta_lite':
            t, t_lo, t_hi, meta = 0, 0, 0, 0
            #t, t_lo, t_hi, meta = eta_lite(d)
        case 'eta_gam':
            t, t_lo, t_hi, meta = 0, 0, 0, 0
            #t, t_lo, t_hi, meta = eta_gam(d)
        case _:
            t, t_lo, t_hi, meta = 0, 0, 0, 0

    return round(t, 1), round(t_lo, 1), round(t_hi, 1), meta


def co_est(d, mod):
    """
    Dispatch CO2 estimation to requested model
    """
    match mod:
        case 'co_simple':
            co, co_lo, co_hi, meta = co_simple(d)
        case 'co_lite':
            co, co_lo, co_hi, meta = 0, 0, 0, 0
            #co, co_lo, co_hi, meta = co_lite(d)
        case 'co_gam':
            co, co_lo, co_hi, meta = 0, 0, 0, 0
            #co, co_lo, co_hi, meta = co_gam(d)
        case _:
            co, co_lo, co_hi, meta = 0, 0, 0, 0

    return round(co), round(co_lo), round(co_hi), meta


def route_est(d, conf):
    """
    Dispatch route estimation to requested service
    """
    match conf["service"]:
        case 'route_streetmap':
            route = route_streetmap(d, conf)
        case 'route_openroute':
            route = 0
            #route = route_openroute(d, conf)
        case 'route_googlemaps':
            route = 0
            #route = route_googlemaps(d, conf)
        case _:
            route = 0

    return route


def region(lat, lon):
    """
    Determine country, NUTS region, and closest postal code, zip,
    using (lat, lon) -coordinates
    """
    zip = '00100'
    # zip = open_street(lat, lon)

    country = 'FI'
    nuts2 = 'FI2'
    nuts3 = 'FI33'
    # country, nuts2, nuts3 = region_nuts(lat, lon)

    reg = {"country": country, "zip": zip, "nuts2": nuts2, "nuts3": nuts3}

    return reg

def dist(d):
    """
    Distance [km] between two (lat, lon) -coordinates
    """
    from math import sin, cos, sqrt, atan2, radians

    lat1 = radians(d['lat1'])
    lon1 = radians(d['lon1'])

    lat2 = radians(d['lat2'])
    lon2 = radians(d['lon2'])

    lond = lon2 - lon1
    latd = lat2 - lat1

    a = sin(latd/2)**2 + cos(lat1) * cos(lat2) * sin(lond/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    r = 6373.0 # earth radius [km]
    dist = round(r * c)

    log.debug('dist = %i', dist)

    return dist


def price_gam(d, price_km=2, price_min=50, err=0.1):
    """
    ML based transportation price estimate.
    GAM model uses EU statistics, price-distance matrix between NUTS regions.
    """
    #l = dist(d)

    from_reg = region(lat=d["lat1"], lon=d["lon1"])
    to_reg   = region(lat=d["lat2"], lon=d["lon2"])

    log.debug('from: %s', from_reg)
    log.debug('to  : %s', to_reg)

    p, p_lo, p_hi, meta = 0, 0, 0, 0
    #p, p_lo, p_hi = pridict(model, df)

    return round(p), round(p_lo), round(p_hi), meta


def price_simple(d, price_km=2, price_min=50, err=0.1):
    """
    Simplistic transportation price estimate
    price, p [EUR] =  straight_line(length, ln [km], price/km [EUR/km], price_min [EUR])
    """
    ln = dist(d)

    p = price_km * ln + price_min
    p_lo = p - p * err
    p_hi = p + p * err

    meta = 0

    return round(p), round(p_lo), round(p_hi), meta


def price_lite(d, price_km=2, price_min=50, err=0.1):
    """
    Lite transportation price estimate using EU transportation data for NUTS regions
    price, p [EUR] =  straight_line(length, l [km], price/km [EUR/km], price_min [EUR])
    """

    r = nuts_intel(dd, dp, d["lat1"], d["lon1"], d["lat2"], d["lon2"])
    p, p_hi, p_lo, meta = price_nuts(r)

    return round(p), round(p_lo), round(p_hi), meta

def eta_simple(d, v=80, err=0.1):
    """
    Simplistic transportation time estimate.
    time t [h], lane length ln [km], and speed v [km/h]
    """
    ln = dist(d)

    t = ln / v
    t_lo = t - t * err
    t_hi = t + t * err

    meta = 0
    return round(t, 1), round(t_lo, 1), round(t_hi, 1), meta


def co_simple(d, c=100, err=0.2):
    """
    Simplistic transportation CO2 [g] estimate
    distance d [km], CO2/km c [g/km]
    """
    ln = dist(d)

    c = d.get('co', c) # get co from the dict d, or use the default value c

    co = c * ln
    co_lo = co - co * err
    co_hi = co + co * err

    meta = 0

    return round(co), round(co_lo), round(co_hi), meta


def route_streetmap(d, conf):
    """
    Route calculation using streetmap
    """
    #l = dist(d)

    route = 0

    return route


def closest_nuts(d, lat, lon):
  """
  Find the NUTS region closest to (lat, lon)
  """
  #from scipy.spatial.distance import pdist
  from geopy.distance import geodesic
  #import numpy as np
  la = lat
  lo = lon

  def dist(r, la, lo):
    loc1 = (la, lo)
    loc2 = (r['lat'], r['lon'])
    try:
      ds = (geodesic(loc1, loc2).kilometers)
    except Exception as e:
      log.ERROR(e.message)

    return ds

  print(la, lo)
  d['dist'] = d.apply(lambda r: dist(r, la, lo), axis = 1)
  d = d.round({'dist':0})
  dd = d.sort_values(by = ['dist'])
  return dd[:1] # dd[1:6]


def nuts_intel(dd, dp, lat1, lon1, lat2, lon2):
  """
  Access price data using closest NUTS2-region, dd.
  1st NUTS3 (from, to) regions are determined from (lat, lon)
  """
  nc1 = closest_nuts(dd, lat=lat1, lon=lon1) # NUTS3
  nc2 = closest_nuts(dd, lat=lat2, lon=lon2)
  n1 = nc1['id_nuts'].values[0][0:4]  # NUTS3 nuts NUTS2 conversion
  n2 = nc2['id_nuts'].values[0][0:4]  # pick 4 first letters
  dp1 = dp[dp['start_nuts'] == n1 ] # filter
  dp2 = dp1[dp1['end_nuts'] == n2]
  return dp2


def round_base(x, base=5):
  """
  Round x to closest integer using base.
  For example round_base(123, 5)=125.
  """
  return base * round(x / base)


def price_nuts(r, err_p=0.15, base=10):
  """
  Estimate price [EUR] from NUT2 region to other
  """
  p = r['total_cost'].values[0]
  p_lo = p - err_p * p
  p_hi = p + err_p * p

  #r = r.reset_index(drop=True)
  meta = r.to_dict("records")

  return round_base(p, base), round_base(p_lo, base), round_base(p_hi, base), meta


def eta_nuts(r, err_p=0.15):
  """
  Estimate time on road [h] from NUTS2 region to other
  """
  t = r['time_road'].values[0]
  t_lo = t - err_p * t
  t_hi = t + err_p * t

  meta = 0

  return round(t, 1), round(t_lo, 1), round(t_hi, 1), meta
