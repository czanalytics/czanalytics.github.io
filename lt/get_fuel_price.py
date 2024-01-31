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

