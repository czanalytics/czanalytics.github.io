# lane.py implements api.py endpoints
#
# https://apiflask.com/api/app/
# https://github.com/Fischerfredl/flask-expects-json
# https://lovelace.oulu.fi/ohjelmoitava-web/programmable-web-project-spring-2019/implementing-rest-apis-with-flask/
# curl https://stackoverflow.com/questions/52133268/flask-get-requests-with-json-parameter-using-curl
# https://stackoverflow.com/questions/13081532/return-json-response-from-flask-view
# https://www.toptal.com/python/in-depth-python-logging

import logging as log # log.debug/info/warning 
import json
#import numpy as np
import pandas as pd
from geopy.distance import geodesic
import datetime

#import net
from net import net_test

#import warnings
#warnings.simplefilter(action='ignore', category=FutureWarning)

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
##conf_model = {'price': 'price_lite', 'eta': 'eta_simple','co': 'co_simple'}
#conf_model = {'price': 'price_simple', 'eta': 'eta_simple','co': 'co_simple'} # simple
#conf_model = {'price': 'price_lite', 'eta': 'eta_lite','co': 'co_lite'}
#conf_model = {'price': 'price_gam', 'eta': 'eta_gam','co': 'co_gam'}          # gam
#conf_model = {'price': 'price_automl', 'eta': 'eta_automl','co': 'co_automl'} # automl

# fuel conf
conf_fuel = {'price': 'fuel_simple'}

# bundling conf
conf_bundle= {'routing': 'picat', 'demo':'demo1'}
#conf_bundle= {'routing': 'picat', 'demo':'demo2'}
#conf_bundle= {'routing': 'google', 'demo':'demo3'} # TBD

# route conf TBD
conf_route = {'service': 'route_streetmap', 'foo': 'bar'}
#conf_route = {'service': 'route_openroute'}
#conf_route = {'service': 'route_googlemaps'}

# routing conf TBD
conf_routing = {'service': 'routing_consolidate', 'foo': 'bar'}
#conf_routing = {'service': 'routing_multimodal'}
#conf_routing = {'service': 'routing_fleet'}

# management confs TBD
conf_config = {'config': 'foo'} # manage these configs as files
conf_status = {'status': 'foo'}
conf_report = {'report': 'foo'}

# integrated config
conf = {'version':  0.06,
        'app_ip':   '0.0.0.0',
        #'app_port':    3333,    #prod
        'kb_port':     5555,
        'bundle_port': 6666,
        'fuel_port':   7777,
        'app_port':    8888,     #dev
        'schema':   conf_schema,
        'data':     conf_data,
        'model':    conf_model,
        'route':    conf_route,
        'routing':  conf_routing,
        'bundle':   conf_bundle,
        'fuel':     conf_fuel,
        'config':   conf_config,
        'status':   conf_status,
        'report':   conf_report
        }


lv = log.DEBUG
#log.basicConfig(format='%(asctime)s, %(name)s, %(levelname)s, %(funcName)s:%(lineno)s, %(message)s', level=lv)
log.basicConfig(format='%(asctime)s, %(name)s, %(levelname)s: %(message)s, %(funcName)s:%(lineno)s', level=lv)
#log.basicConfig(format='%(asctime)s, %(levelname)s, %(message)s', level=lv)

dp = pd.read_csv("./nuts.csv") # data for lite-models
dd = pd.read_csv("./nuts_centroid.csv")

#log.INFO('data read')

def get_conf():
 with open('./conf_lite.json', 'r') as JSON:
       dic = json.load(JSON)
 #key = str(2); print(dic); print(dic["1"]); print(dic[key]); print(dic["3"]**2)
 return dic

#con = get_conf()

# ----

# get_fuel_price.py 
# steps: clean > get data > select data from Excel > save to csv

import subprocess

def runcmd(cmd, verbose = False, *args, **kwargs):

    process = subprocess.Popen(
        cmd,
        stdout = subprocess.PIPE,
        stderr = subprocess.PIPE,
        text = True,
        shell = True
    )
    std_out, std_err = process.communicate()
    if verbose:
        print(std_out.strip(), std_err)
    pass

#runcmd('echo "Hello, World!"', verbose = True)

import pandas as pd
import warnings

warnings.simplefilter("ignore")

def fuelPriceRead(f, sheet='Weekly Prices'):
  d = pd.read_excel(f, sheet_name = sheet)
  #d.columns = d.iloc[3] # pick the header from the nth line
  #d.drop(d.index[0:4], inplace=True) # remove the leading empty line
  d = d.iloc[:, [0, 2, 3, 7]] # pick columns
  d.columns = ["date", "country", "fuel", "price"] # rename
  return d[:-2] # skip the empty last rows

def fuelPriceEdit(d):
  d.dropna()
  d['date'] = pd.to_datetime(d['date'], format='%Y-%m-%d %H:%M:%S')

  d['price'] = d['price'].astype(str).str.replace(',', '') # clean
  d['price'] = d['price'].astype(str).str.replace('N.A', '0') #
  d['price'] = d['price'].astype('float')
  d['price'] = d['price']/1000 # units to liters
  d = d.round(2)

  d = d[(d['price'] > 0)] # reasonable constraint
  # d = d.drop('rate', axis=1)
  return d

# ----

def fuel_est(d, mod):
    """
    Dispatch fuel price estimates to requested model
    """

    fd = {"foo": "bar"}

    match mod:
        case 'fuel_simple':
            fuel_dict, doc = fuel_simple(d)
        case 'fuel_lite':
            fuel_dict, doc = fd, "null"
            #fuel_dict, doc = fuel_lite(d)
        case _:
            fuel_dict, doc = fd, "null"
            #log.ERROR('unknown fuel model') 

    log.debug('fuel_price_est: request %s', d)

    return fuel_dict, doc


def fuel_simple(d):
    """
    Provide latest fuel price info from weekly EU statistics source.
    """

    # steps
    runcmd('rm -f /home/fuel.xlsx', verbose=True) # clean
    runcmd('wget -O /home/fuel.xlsx https://ec.europa.eu/energy/observatory/reports/latest_prices_raw_data.xlsx', verbose=True)

    d = fuelPriceRead("/home/fuel.xlsx")
    d = fuelPriceEdit(d)
    #d.info()

    fo = '/home/' + 'fuel.csv'
    d.to_csv(fo, index=False, encoding='utf-8')

    date_tag = d['date'][0].strftime('%y-%m-%d')
    fo = '/home/' + 'fuel-' + date_tag + '.csv'
    d.to_csv(fo, index=False, encoding='utf-8')

    with open('/home/fuel.csv','r') as f:
        doc = f.read()

    doc = "Weekly EU stats https://ec.europa.eu/energy/observatory/reports/latest_prices_raw_data.xlsx"

    import csv

    with open('/home/fuel.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [row for row in reader]

    with open('/home/fuel.json', 'w') as jsonfile:
        json.dump(data, jsonfile)

    f = open('/home/fuel.json')
    fuel_dict = json.load(f)
    #fuel_dict =  {"foo":"bar"}
    f.close()

    return fuel_dict, doc
    #return round(p, 1), round(p_lo, 1), round(p_hi, 1), doc


def price_est(d, mod):
    """
    Dispatch price calculation to requested model
    """
    match mod:
        case 'rprice_simple':
            p, p_lo, p_hi, doc = price_simple(d)
        case 'price_lite':
            p, p_lo, p_hi, doc = price_lite(d)
        case 'price_gam':
            p, p_lo, p_hi, doc = 0, 0, 0, ""
            #p, p_lo, p_hi, doc = price_gam(d)
        case 'price_automl':
            p, p_lo, p_hi, doc = 0, 0, 0, ""
            #p, p_lo, p_hi, doc = price_automl(d)
        case _:
            p, p_lo, p_hi, doc = 0, 0, 0, ""
            #log.ERROR('unknown model') # fails

    log.debug('price_est: request %s', d)

    return p+0.01, p_lo+0.01, p_hi+0.01, doc


def eta_est(d, mod):
    """
    Dispatch ETA calculation to requested model
    """
    # structural pattern mathing, https://peps.python.org/pep-0622/
    match mod:
        case 'eta_simple':
            t, t_lo, t_hi, doc = eta_simple(d)
        case 'eta_lite':
            t, t_lo, t_hi, doc = eta_lite(d)
        case 'eta_gam':
            t, t_lo, t_hi, doc = 0, 0, 0, ""
            #t, t_lo, t_hi, doc = eta_gam(d)
        case _:
            t, t_lo, t_hi, doc = 0, 0, 0, ""

    log.debug('eta_est: request %s', d)

    return t+0.01, t_lo+0.01, t_hi+0.01, doc


def co_est(d, mod):
    """
    Dispatch CO2 estimation to requested model
    """
    match mod:
        case 'co_simple':
            co, co_lo, co_hi, doc = co_simple(d)
        case 'co_lite':
            co, co_lo, co_hi, doc = 0, 0, 0, ""
            #co, co_lo, co_hi, doc = co_lite(d)
        case 'co_gam':
            co, co_lo, co_hi, doc = 0, 0, 0, ""
            #co, co_lo, co_hi, doc = co_gam(d)
        case _:
            co, co_lo, co_hi, doc = 0, 0, 0, ""

    log.debug('co_est: request %s', d)

    return co+0.01, co_lo+0.01, co_hi+0.01, doc


def route_est(d, conf):
    """
    Dispatch route estimation to requested service
    """
    r0 = 0 # default

    match conf["service"]:
        case 'route_streetmap':
            r = route_streetmap(d, conf)
        case 'route_openroute':
            #r = route_openroute(d, conf)
            r = r0
        case 'route_googlemaps':
            #r = route_googlemaps(d, conf)
            r = r0
        case _:
            r = r0

    doc = ""
    log.debug('route_est: request %s', d)

    return r, doc


def routing_lane(d, mod):
    """
    Dispatch selected routing service
    """
    r0 = 0 # default

    match mod:
        case 'routing_consolidate':
            r = routing_consolidate(d, 0)
        case 'routing_multimodal':
            #r = routing_multimodal(d, 0)
            r = r0
        case 'routing_fleet':
            #r = routing_fleet(d, 0)
            r = r0
        case _:
            r = r0

    doc = ""
    log.debug('routing_est: request %s', d)
    log.debug('routing_est: r %s', r)

    return r, doc


def config_lane(d, cnf):
    """
    Configuration management. List and adjust configuration.
    """
    # TBD read conf-file. List/edit, and save/export conf.
    # add pricing section

    r = {"new_conf": "yeah!"}
    r = cnf

    return r


def status_lane(d, cnf):
    """
    Service status
    """

    r = {"status": "yeah!"}
    return r


def report_lane(d, cnf):
    """
    Report generation
    """

    r = {"report": "yeah!"}
    return r


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

    #log.debug('dist = %i', dist)

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

    p, p_lo, p_hi = 0, 0, 0
    #p, p_lo, p_hi = pridict(model, df)

    doc = ""

    return round(p, 1), round(p_lo, 1), round(p_hi, 1), doc


def price_simple(d, price_km=2, to_road_dist=1.2, price_min=20, err=0.15):
    """
    Simplistic transportation price estimate
    price, p [EUR] =  straight_line(length, ln [km], price/km [EUR/km], price_min [EUR])
    road distance = gps-distance * to_road_dist = 1.2 by default
    """
    ln = dist(d) * to_road_dist

    p = price_km * ln + price_min
    p_lo = p - p * err
    p_hi = p + p * err

    doc = ""

    return round(p, 1), round(p_lo, 1), round(p_hi, 1), doc


def price_lite(d, price_km=2, price_min=50, err=0.1):
    """
    Lite transportation price [EUR] estimate
    using EU transportation data for NUTS regions.
    """
    r = nuts_intel(d, dd, dp)

    p, p_lo, p_hi, doc = price_nuts(r)

    return round(p, 1), round(p_lo, 1), round(p_hi, 1), doc


def eta_simple(d, v=80, to_road_dist=1.2, err=0.15):
    """
    Simplistic transportation time estimate.
    time t [h], lane length ln [km], and speed v [km/h]
    """
    ln = dist(di) * to_road_dist

    t = ln / v
    t_lo = t - t * err
    t_hi = t + t * err

    doc = ""

    return round(t, 1), round(t_lo, 1), round(t_hi, 1), doc


def eta_lite(d, v=80, err=0.10):
    """
    Lite transportation time [h] estimate
    using EU transportation data for NUTS regions.
    """
    r = nuts_intel(d, dd, dp)
    t, t_lo, t_hi, doc = eta_nuts(r)

    return round(t, 1), round(t_lo, 1), round(t_hi, 1), doc


def co_simple(d, c=100.0, to_road_dist=1.2, err=0.2):
    """
    Simplistic transportation CO2 [g] estimate
    distance d [km], CO2/km c [g/km]
    """
    ln = dist(d) * to_road_dist

    c = d.get('co', c) # get co from the dict d, or use the default value c

    co = c * ln
    co_lo = co - co * err
    co_hi = co + co * err

    doc = ""

    return round(co, 1), round(co_lo, 1), round(co_hi, 1), doc


def route_streetmap(d, conf):
    """
    Route calculation using streetmap
    """
    #l = dist(d)

    route = 0

    return route


def routing_consolidate(d, cnf):
    """
    Consolidate is a car relocation task.
    Car-carriers, in coordination, collect/deliver cars.
    """

    r0, st = net_test(dd, dp)

    dd.to_csv("./net.csv", sep=',', index=False, encoding='utf-8')

    log.debug('routing_consolidate: net %s', r0)
    r = 0

    return r
    #return st # nan in df makes json fails?


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

  #print(la, lo)

  d['dist'] = d.apply(lambda r: dist(r, la, lo), axis = 1)
  d = d.round({'dist':0})
  dd = d.sort_values(by = ['dist'])
  return dd[:1] # dd[1:6]


def nuts_intel(d, dd, dp):
  """
  Access price data using closest NUTS2-region, dd.
  1st NUTS3 (from, to) regions are determined from (lat, lon)
  """
  x = 0.01

  nc1 = closest_nuts(dd, lat=d["lat1"], lon=d["lon1"]) # NUTS3
  nc2 = closest_nuts(dd, lat=d["lat2"], lon=d["lon2"])

  n1 = nc1['id_nuts'].values[0][0:4]  # NUTS3 nuts NUTS2 conversion
  n2 = nc2['id_nuts'].values[0][0:4]  # pick 4 first letters

  dp1 = dp[dp['start_nuts'] == n1 ] # filter
  r = dp1[dp1['end_nuts'] == n2].copy()

  d1 = nc1['dist'].values[0]
  d2 = nc2['dist'].values[0]

  r['lane_da'] = d.get('da')
  r['lane_db'] = d.get('db', d.get('da'))  # if db is missing use da
  r['lane_ta'] = d.get('ta', '00:00') # 00:00 is default
  r['lane_tb'] = d.get('tb', '24:00')

  r['lane_err1'] = d1+x # add metadata
  r['lane_err2'] = d2+x

  r['lane_dist'] = dist({'lat1': d["lat1"], 'lon1': d["lon1"], 'lat2':d["lat2"], 'lon2':d["lon2"]})+x

  # round response data
  r['all_distancecosts'] = round_base(r['all_distancecosts'])+x
  r['all_timecosts'] =  round_base(r['all_timecosts'])+x
  r['distance_geodesic'] = round(r['distance_geodesic'])+x
  r['distance_road'] = round(r['distance_road'])+x
  r['fuel'] = round(r['fuel'])+x
  r['taxes'] = round_base(r['taxes'])+x
  r['tolls'] = round_base(r['tolls'])+x
  r['total_cost'] = round_base(r['total_cost'])+x
  r['vignettecost'] = round_base(r['vignettecost'])+x
  r['wages'] = round_base(r['wages'], 5)+x

  log.debug('nuts_intel = %s', r)

  return r


def round_base(x, base=5):
  """
  Round x to closest integer using base.
  For example round_base(123, 5)=125.
  """
  xx = base * round(x / base)

  return round(xx, 1)


def price_nuts(r, err_p=0.10, base=10, price_min=20):
  """
  Estimate price [EUR] from NUT2 region to other
  """
  x = 0.01
  c = corr_price(r) # correction components

  r['lane_corr'] = "['corr_dist', 'corr_fuel', 'corr_index', 'corr_tight']"

  corr_dist  = round(r.get('distance_road') * (c.get('corr_dist')  - 1.00))+x
  corr_fuel  = round(r.get('fuel')          * (c.get('corr_fuel')  - 1.00))+x
  corr_index = round(r.get('total_cost')    * (c.get('corr_index') - 1.00))+x
  corr_month = round(r.get('total_cost')    * (c.get('corr_month') - 1.00))+x
  corr_day   = round(r.get('total_cost')    * (c.get('corr_day')   - 1.00))+x
  corr_rush  = round(r.get('total_cost')    * (c.get('corr_rush')  - 1.00))+x

  corr_tot = corr_dist + corr_fuel + corr_index + corr_rush
  corr_tot = corr_tot.iloc[0]

  #log.debug('corr_tot = %s', corr_tot)

  r['lane_corr_dist']  = corr_dist
  r['lane_corr_fuel']  = corr_fuel
  r['lane_corr_index'] = corr_index
  r['lane_corr_month'] = corr_month
  r['lane_corr_day']   = corr_day
  r['lane_corr_rush']  = corr_rush

  r['lane_corr_tot'] = round_base(corr_tot)
  p = round(r.get('total_cost').iloc[0]) + corr_tot

  p = max(price_min, p)

  e = err_price(r) # error components

  r['lane_err']        = "['err_base', 'err_dist', 'err_loc', 'err_future']"

  err_base   = round_base(p * e.get('err_base'))+x
  err_dist   = round_base(p * e.get('err_dist') / r.get('distance_road'))+x
  err_loc    = round_base(p * e.get('err_loc')  / r.get('distance_road'))+x
  err_future = round_base(p * e.get('err_future'))+x

  err = err_base + err_dist + err_loc + err_future
  err = err.iloc[0]

  r['lane_err_base']   = err_base
  r['lane_err_dist']   = err_dist
  r['lane_err_loc']    = err_loc
  r['lane_err_future'] = err_future

  r['lane_err_tot'] = round_base(err)+x

  p_lo = max(price_min, p - err)
  p_hi = p + err

  log.debug('price = %s (%s, %s)', round(p, 1), round(p_lo, 1), round(p_hi, 1))

  doc = r.to_dict("records")

  return round_base(p, base), round_base(p_lo, base), round_base(p_hi, base), doc


def eta_nuts(r, err_p = 0.15):
  """
  Estimate time on road [h] from NUTS2 region to other
  """
  x = 0.01
  t = r['time_road'].values[0]+x
  t_lo = t - err_p * t + x
  t_hi = t + err_p * t + x

  doc = r.to_dict("records")

  return round(t, 1), round(t_lo, 1), round(t_hi, 1), doc


def corr_price(r):
  """
  Corrections for tuning price calculation.
  The approach is simplistic, heuristic, and qualitative, at best,
  so evidence-based approach should be used when possible.
  For each component, the correction is 0% by default.
  Correction 1.05 mean 5% price increase, and 0.90 means -10% reduction.
  """
  import datetime
  from datetime import date
  from datetime import datetime

  da = r['lane_da'].values[0] # ok

  # YYYY-MM-DD
  # 0123456789
  yyyy = int(da[0:4]); mm = int(da[5:7]); dd = int(da[8:10]) # ! index?
  #yyyy = int("20" + da[0:2]); mm = int(da[3:5]); dd = int(da[6:8])

  dur = date.today() - date(yyyy, mm, dd)

  log.debug('corr_price: yyyy %s, mm %s, dd %s, dur %s', yyyy, mm, dd, dur.days)

  conf_lite = get_conf() # json
  key_day = 4 # TBD
  key_month = 7

  corr_dist  =  r.get('lane_dist') / r.get('distance_geodesic')
  corr_fuel  = 1.00
  corr_wages = 1.00
  corr_index = 0.90
  corr_hist  = 1.00
  corr_month = conf_lite["corr_month"][key_month]
  corr_day   = conf_lite["corr_day"][key_day]
  corr_rush  = 1.00 + 0.05 / (1 + abs(dur.days)**2) - 0.05 # 1 day adds 5%, 2 days 1%, and 3- ~0% 
  corr_tight = 1.00

  corrs = {
      "corr_dist":corr_dist, "corr_fuel":corr_fuel,
      "corr_wages":corr_wages, "corr_index":corr_index,
      "corr_hist":corr_hist, "corr_month":corr_month, "corr_day":corr_day,
      "corr_rush":corr_rush, "corr_tight":corr_tight}

  return corrs


def err_price(r):
  """
  Error estimation for price calculation.
  The approach is simplistic, heuristic, and qualitative, at best,
  so proper statistical approach should be used when possible.
  By default the error component is 0.00, meaning no error, while 0.10 means 10% price error.
  """
  import datetime
  from datetime import date
  from datetime import datetime

  da = r['lane_da'].values[0] # ok

  #log.debug('da = %s', da)

  yyyy = int(da[0:4]); mm = int(da[5:7]); dd = int(da[8:10])
  #yyyy = int("20" + da[0:2]); mm = int(da[3:5]); dd = int(da[6:8])

  dur = date.today() - date(yyyy, mm, dd)
  dur_days = dur.days
  dur_weeks  = round(dur_days/7, 1)

  log.debug('err_price: yyyy %s, mm %s, dd %s, dur %s', yyyy, mm, dd, dur.days)

  x = 0.001
  corr_dist  =  r.get('lane_dist') / r.get('distance_geodesic')
  err_base   = 0.10 + dur_weeks * 0.0001+0.01 # default
  err_dist   = abs(corr_dist - 1.00) * r.get('distance_road')+x  # km
  err_loc    = (r.get('lane_err1') + r.get('lane_err2')) / 2 +x  # km 
  err_prior  = 0.00 + x
  err_env    = 0.00 + x# TBD weather, for ETA estimates too!
  err_future = 0.00 + x# weeks in future

  errs = {
      "err_base":err_base, "err_dist":err_dist, "err_loc": err_loc,
      "err_prior":err_prior, "err_env":err_env, "err_future":err_future}

  return errs
