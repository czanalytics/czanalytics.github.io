# bundle.py for routing  

import logging as log
import json

from lane import runcmd

lv = log.DEBUG
log.basicConfig(format='%(asctime)s, %(name)s, %(levelname)s: %(message)s, %(funcName)s:%(lineno)s', level=lv)


def bundle_est(d, mod):
    """
    Dispatch bundling to requested backend.
    """

    fd = {"foo": "bar"}

    match mod:
        case 'picat':
            plan_dict, doc = plan_picat(d)
        case 'google':
            plan_dict, doc = fd, "null"
            #plan_dict, doc = plan_google(d) # TBD
        case _:
            plan_dict, doc = fd, "null"
            #log.ERROR('unknown bundle plan') 

    log.debug('bundle_est: request %s', d)

    return plan_dict, doc


def demo_est(d, mod):
    """
    Dispatch the requested demo.
    """

    fd = {"foo": "bar"}

    match mod:
        case 'demo1':
            demo_dict, doc = demo1(d)
        case 'demo2':
            demo_dict, doc = demo2(d)
        case 'demo3':
            demo_dict, doc = fd, "null"
            #demo_dict, doc = demo3(d)
        case _:
            demo_dict, doc = fd, "null"
            #log.ERROR('unknown demo') 

    log.debug('demo_est: request %s', d)

    return demo_dict, doc


def plan_picat(d):
    """
    """

    runcmd("rm -f /Picat/plan.txt")

    runcmd('cd Picat; ./picat bundle.pi >> plan.txt', verbose=True)

    with open('/Picat/plan.txt','r') as f:
        doc = f.read()
    #doc = "foo & bar"
    doc2 = doc.replace("'", "\"")
    d = json.loads(doc2)
    d = dict(sorted(d.items()))
    return d, doc


def plan_google(d):
    """
    TBD
    """
    d = {"foo": "bar"}
    doc = "foo & bar"

    return d, doc


def demo3(d):
    """
    TBD
    """
    d = {"foo": "bar"}
    doc = "foo & bar"

    return d, doc


def demo2(d):
    """
    """
    d = {"foo": "bar"}
    doc = "foo & bar"

    return d, doc


def demo1(d):
    """
    Introduce Picat for Pickup and Delivery Problem, PDP.
    Output log from Picat is returned.
    """

    runcmd("ls -lat /Picat")

    runcmd("rm -f /Picat/demo1.txt")

    runcmd('cd Picat; ./picat pdp.pi >> demo1.txt', verbose=True)

    with open('/Picat/demo1.txt','r') as f:
        doc = f.read()
    #doc = "foo & bar"

    #doc2 = doc.replace("'", "\"")
    #d = json.loads(doc2)
    d = {"foo": "bar"}

    return d, doc


"""
def fuel_simple(d):
    #Provide latest fuel price info from weekly EU statistics source.

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

# steps
runcmd('rm -f /home/fuel.xlsx', verbose=True) # clean
runcmd('wget -O /home/fuel.xlsx https://ec.europa.eu/energy/observatory/reports/latest_prices_raw_data.xlsx', verbose=True)

d = fuelPriceRead("/home/fuel.xlsx")
d = fuelPriceEdit(d)
#d.info()

date_tag = d['date'][0].strftime('%y-%m-%d')
fo = '/home/' + 'fuel-' + date_tag + '.csv'

d.to_csv(fo, index=False, encoding='utf-8')
f = '/home/' + 'fuel.csv' # continuity: the latest price has same name
d.to_csv(f, index=False, encoding='utf-8')
"""
