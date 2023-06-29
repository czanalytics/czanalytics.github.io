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
import json

schema_api = {'type': 'object',
          'properties': {'date': {'type': 'string'},
                         'from_lat': {'type': 'float'}},
                         'required': ['date', 'from_lat']
          }

mods = {'price': 'price_simple', 'eta': 'eta_simple','co': 'co_simple' }
#mods = {'price': 'price_lite', 'eta': 'eta_lite','co': 'co_lite' }
#mods = {'price': 'price_gam', 'eta': 'eta_gam','co': 'co_gam' }
#mods = {'price': 'price_automl', 'eta': 'eta_automl','co': 'co_automl' }

conf = {'version': 0.27,
        'app_ip': '0.0.0.0',
        'app_port': 3333,
        'schema': schema_api,
        'model': mods
        }

l = log.DEBUG
#l = log.ERROR
log.basicConfig(format='%(asctime)s, %(name)s, %(levelname)s, %(funcName)s:%(lineno)s, %(message)s', level=l)
#log.basicConfig(format='%(asctime)s, %(levelname)s, %(message)s', level=log.DEBUG)


def price_est(d, mod):
    """
    Dispatch price calculation to requested model
    """
    match mod:
        case 'price_simple':
            p, p_lo, p_hi = price_simple(d)
        case 'price_lite':
            p, p_lo, p_hi = 0, 0, 0
            #t, t_lo, t_hi = price_lite(d)
        case 'price_gam':
            p, p_lo, p_hi = 0, 0, 0
            #t, t_lo, t_hi = price_gam(d)
        case 'price_automl':
            p, p_lo, p_hi = 0, 0, 0
            #p, p_lo, p_hi = price_automl(d)
        case _:
            p, p_lo, p_hi = 0, 0, 0
            #log.ERROR('unknown model') # fails

    return round(p), round(p_lo), round(p_hi)


def eta_est(d, mod):
    """
    Dispatch ETA calculation to requested model
    """
    # structural pattern mathing, https://peps.python.org/pep-0622/
    match mod:
        case 'eta_simple':
            t, t_lo, t_hi = eta_simple(d)
        case 'eta_lite':
            t, t_lo, t_hi = 0, 0, 0
            #t, t_lo, t_hi = eta_lite(d)
        case 'eta_gam':
            t, t_lo, t_hi = 0, 0, 0
            #t, t_lo, t_hi = eta_gam(d)
        case _:
            t, t_lo, t_hi = 0, 0, 0

    return round(t, 1), round(t_lo, 1), round(t_hi, 1)


def co_est(d, mod):
    """
    Dispatch CO2 estimation to requested model
    """
    match mod:
        case 'co_simple':
            co, co_lo, co_hi = co_simple(d)
        case 'co_lite':
            co, co_lo, co_hi = 0, 0, 0
            #co, co_lo, co_hi = co_lite(d)
        case 'co_gam':
            co, co_lo, co_hi = 0, 0, 0
            #co, co_lo, co_hi = co_gam(d)
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
    l = dist(d)

    from_reg = region(lat=d["from_lat"], lon=d["from_lon"])
    to_reg = region(lat=d["to_lat"], lon=d["to_lon"])

    log.debug('from: %s', from_reg)
    log.debug('to  : %s', to_reg)

    p, p_lo, p_hi = 0, 0, 0
    #p, p_lo, p_hi = pridict(model, df)

    return round(p), round(p_lo), round(p_hi)


def price_simple(d, price_km=2, price_min=50, err=0.1):
    """
    Simplistic transportation price estimate
    price, p [EUR] =  straight_line(length, l [km], price/km [EUR/km], price_min [EUR])
    """
    l = dist(d)

    p = price_km * l + price_min
    p_lo = p - p * err
    p_hi = p + p * err

    return round(p), round(p_lo), round(p_hi)


def eta_simple(d, v=80, err=0.1):
    """
    Simplistic transportation time estimate.
    time t [h], lane length l [km], and speed v [km/h]
    """
    l = dist(d)

    t = l / v
    t_lo = t - t * err
    t_hi = t + t * err

    return round(t, 1), round(t_lo, 1), round(t_hi, 1)


def co_simple(d, c=100, err=0.2):
    """
    Simplistic transportation CO2 [g] estimate
    distance d [km], CO2/km c [g/km]
    """
    l = dist(d)

    co = c * l
    co_lo = co - co * err
    co_hi = co + co * err

    return round(co), round(co_lo), round(co_hi)

