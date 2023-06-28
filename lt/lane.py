# lane.py
# functionality for api.py endpoints
#
# https://apiflask.com/api/app/
# https://github.com/Fischerfredl/flask-expects-json
# https://lovelace.oulu.fi/ohjelmoitava-web/programmable-web-project-spring-2019/implementing-rest-apis-with-flask/
# pip install jsonschema ?
# curl https://stackoverflow.com/questions/52133268/flask-get-requests-with-json-parameter-using-curl
# https://stackoverflow.com/questions/13081532/return-json-response-from-flask-view

def dist(d):
    from math import sin, cos, sqrt, atan2, radians
    lat1 = radians(d['from_lat'])
    lon1 = radians(d['from_lon'])
    lat2 = radians(d['to_lat'])
    lon2 = radians(d['to_lon'])

    # Approximate radius of earth in km
    R = 6373.0

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    dist = R * c
    return round(dist)

def price_est(dj, price_km=2, price_min=100, err=0.1):
    """
    Simplistic transportation price estimate
    price, p [EUR] =  straight_line(distance, d [km], price/km [EUR/km], price_min [EUR])
    """
    #d = dj['distance']
    d = dist(dj)
    p = price_km * d + price_min
    p_lo = p - p * err
    p_hi = p + p * err

    return round(p), round(p_lo), round(p_hi)

def eta_est(dj, v=100, err=0.1):
    """
    Simplistic transportation time estimate
    time, t [h] = distance, d [km] / speed, v [km/h]
    """
    d = dist(dj)
    #d = dj['distance']
    t = d / v
    t_lo = t - t * err
    t_hi = t + t * err
    return round(t, 1), round(t_lo, 1), round(t_hi, 1)

def co_est(dj, c=100, err=0.2):
    """
    Simplistic transportation CO2 exhaust estimate
    CO2 [g] =  distance, d [km] * CO2, c [g/km]
    """
    d = dist(dj)
    #d = dj['distance']

    co = d * c
    co_lo = co - co * err
    co_hi = co + co * err
    return round(co), round(co_lo), round(co_hi)

