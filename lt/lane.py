# lane.py
# functions for api.py endpoints
#
# https://apiflask.com/api/app/
# https://github.com/Fischerfredl/flask-expects-json
# https://lovelace.oulu.fi/ohjelmoitava-web/programmable-web-project-spring-2019/implementing-rest-apis-with-flask/
# pip install jsonschema ?
# curl https://stackoverflow.com/questions/52133268/flask-get-requests-with-json-parameter-using-curl
# https://stackoverflow.com/questions/13081532/return-json-response-from-flask-view

# https://www.toptal.com/python/in-depth-python-logging
import logging as log # log.debug/info/warning 

import json

schema_api = {'type': 'object',
          'properties': {'date': {'type': 'string'},
                         'from_lat': {'type': 'float'}},
                         'required': ['date', 'from_lat']
          }

ms = {'price': 'price_simple', 'eta': 'eta_simple','co': 'co_simple' }
#ms = {'price': 'price_lite', 'eta': 'eta_lite','co': 'co_lite' }
#ms = {'price': 'price_gam', 'eta': 'eta_gam','co': 'co_gam' }
#ms = {'price': 'price_automl', 'eta': 'eta_automl','co': 'co_automl' }

conf = {'version': 0.27,
        'app_ip': '0.0.0.0',
        'app_port': 3333,
        'schema': schema_api,
        'model': ms
        }

l = log.DEBUG
#l = log.ERROR
log.basicConfig(format='%(asctime)s, %(name)s, %(levelname)s, %(funcName)s:%(lineno)s, %(message)s', level=l)
#log.basicConfig(format='%(asctime)s, %(levelname)s, %(message)s', level=log.DEBUG)


def price_est(dj, model):
    """
    Dispatch price calculation to requsted model
    """
    match model:
        case 'price_simple':
            p, p_lo, p_hi = price_simple(dj)
        case 'price_lite':
            p, p_lo, p_hi = 0, 0, 0
            #t, t_lo, t_hi = price_lite(dj)
        case 'price_gam':
            p, p_lo, p_hi = 0, 0, 0
            #t, t_lo, t_hi = price_gam(dj)
        case 'price_automl':
            p, p_lo, p_hi = 0, 0, 0
            #p, p_lo, p_hi = price_automl(dj)
        case _:
            p, p_lo, p_hi = 0, 0, 0
            #log.ERROR('unknown model') # fails

    return round(p), round(p_lo), round(p_hi)


def eta_est(dj, model):
    """
    Dispatch ETA calculation to requested model
    """
    # structural pattern mathing, https://peps.python.org/pep-0622/
    match model:
        case 'eta_simple':
            t, t_lo, t_hi = eta_simple(dj)
        case 'eta_lite':
            t, t_lo, t_hi = 0, 0, 0
            #t, t_lo, t_hi = eta_lite(dj)
        case 'eta_gam':
            t, t_lo, t_hi = 0, 0, 0
            #t, t_lo, t_hi = eta_gam(dj)
        case _:
            t, t_lo, t_hi = 0, 0, 0

    return round(t, 1), round(t_lo, 1), round(t_hi, 1)


def co_est(dj, model):
    """
    Dispatch CO2 estimation to requested model
    """
    match model:
        case 'co_simple':
            co, co_lo, co_hi = co_simple(dj)
        case 'co_lite':
            co, co_lo, co_hi = 0, 0, 0
            #co, co_lo, co_hi = co_lite(dj)
        case 'co_gam':
            co, co_lo, co_hi = 0, 0, 0
            #co, co_lo, co_hi = co_gam(dj)
        case _:
            co, co_lo, co_hi = 0, 0, 0

    return round(co), round(co_lo), round(co_hi)


def region(lat, lon):
    """
    Determine country, NUTS region, and closest postal code using (lat, lon) -coordinates
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

    lat1 = radians(d['from_lat'])
    lon1 = radians(d['from_lon'])
    lat2 = radians(d['to_lat'])
    lon2 = radians(d['to_lon'])

    #status = "connection unavailable"
    #log.error("System reported: %s", status)

    # Approximate radius of earth in km
    R = 6373.0

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    dist = round(R * c)

    log.debug('dist = %i', dist)

    return dist


def price_gam(dj, price_km=2, price_min=50, err=0.1):
    """
    ML based transportation price estimate
    price, p [EUR] =  straight_line(distance, d [km], price/km [EUR/km], price_min [EUR])
    """
    d = dist(dj)

    from_reg = region(lat=dj["from_lat"], lon=dj["from_lon"])
    to_reg = region(lat=dj["to_lat"], lon=dj["to_lon"])

    log.debug('from: %s', from_reg)
    log.debug('to  : %s', to_reg)

    p, p_lo, p_hi = 0, 0, 0
    #p, p_lo, p_hi = pridict(model, df)

    return round(p), round(p_lo), round(p_hi)


def price_simple(dj, price_km=2, price_min=50, err=0.1):
    """
    Simplistic transportation price estimate
    price, p [EUR] =  straight_line(distance, d [km], price/km [EUR/km], price_min [EUR])
    """
    d = dist(dj)

    p = price_km * d + price_min
    p_lo = p - p * err
    p_hi = p + p * err

    return round(p), round(p_lo), round(p_hi)


def eta_simple(dj, v=80, err=0.1):
    """
    Simplistic transportation time estimate
    time, t [h] = distance, d [km] / speed, v [km/h]
    """
    d = dist(dj)

    t = d / v
    t_lo = t - t * err
    t_hi = t + t * err

    return round(t, 1), round(t_lo, 1), round(t_hi, 1)


def co_simple(dj, c=100, err=0.2):
    """
    Simplistic transportation CO2 exhaust estimate
    CO2 [g] =  distance, d [km] * CO2, c [g/km]
    """
    d = dist(dj)

    co = d * c
    co_lo = co - co * err
    co_hi = co + co * err

    return round(co), round(co_lo), round(co_hi)

