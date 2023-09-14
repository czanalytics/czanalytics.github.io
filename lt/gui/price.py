# price.py

def approx(x, n=20):
  """Round x to closest n"""

  return round(x/n)*n

def price_est(loc1, loc2, dist = 111, c = 2.0, pro=0.1):
  """Estimate price based on postal code locations."""

  p = dist * c             # mockup
  p_lo = p - pro * p
  p_hi = p + pro * p

  return approx(p), approx(p_lo), approx(p_hi)


import pandas as pd

from pyodide.http import open_url

#url_nuts2 = 'https://raw.githubusercontent.com/czanalytics/multimodal-shipping/main/dat/nuts2.json'
#geo_nuts2= json.loads(open_url(url_nuts2).read())

def get_data():
    url = ("https://raw.githubusercontent.com/czanalytics/multimodal-shipping/main/dat/ODMatrix2021_N2.csv")
    d = pd.read_csv(open_url(url))

    return d

#d_ = d.loc[(d['Origin'] == 'ES70') & (d['Destination'] == 'PT11') ]
#print (d_)


import js
from js import document
from pyodide.ffi import create_proxy

def _flight_mode_change(*args, **kwargs):
  currentMode = document.getElementById("flight-mode-select").value

  currentMode = 'eur'

  if currentMode == 'one':
    document.getElementById("ret").disabled = True
  else:
    document.getElementById("ret").disabled = False


def _book_flight(*args, **kwargs):
  currentMode = document.getElementById("flight-mode-select").value
  currentMode = 'eur'

  loc1 = document.getElementById("dep").value
  loc2 = document.getElementById("ret").value

  price, price_lo, price_hi = price_est(loc1, loc2)
  #price = str(1000); price_lo = 'aaa'; price_hi = 'sssss'

  if currentMode == 'one':
    document.getElementById("flight-info").innerText = f"Departing on {loc1}."
  else:
    document.getElementById("flight-info").innerText = f"{price} EUR ({price_lo}, {price_hi})"

