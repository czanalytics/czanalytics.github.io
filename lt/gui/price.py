# price.py

import json

from pyodide.http import pyfetch

url = "https://chips-generating.runblade.host"

async def login(email, pw):
    print('login')
    ur = "http://127.0.0.1:3333/api/route"
    d = {"id":"230914-001", "da":"23-10-01", "lat1":48.86471, "lon1":2.23901, "lat2":52.36760, "lon2":4.90410, "meta":"loc1-loc2"}
    print(d)

    try:
        response = await pyfetch("https://cdn.jsdelivr.net/pyodide/v0.23.4/full/repodata.json") #ok
        """
        response = await pyfetch(
            url = ur,
            method = "GET",
            headers = {"Content-Type": "application/json", "Api-Key": "s3cr3t_k3y"},
            body = json.dumps(d)
        )
        """
        if response.ok:
            data = await response.json()
            print(data)
            return data
            #return data.get("token")
    except Exception as e:
        print(f" Raising exception ")
    finally:
        return "hello"


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

def get_data():
    url = ("https://raw.githubusercontent.com/czanalytics/multimodal-shipping/main/dat/ODMatrix2021_N2.csv")
    d = pd.read_csv(open_url(url))

    return d

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

  if currentMode == 'one':
    document.getElementById("flight-info").innerText = f"Departing on {loc1}."
  else:
    document.getElementById("flight-info").innerText = f"Price for {loc1} - {loc2} is {price} EUR ({price_lo}, {price_hi})"


async def _lane_api(*args, **kwargs):
  print("main_api()")

  id = "230925-001"
  da = "23-10-01"

  da = str(document.getElementById("da").value)

  payload = {"id": id, "da": da, "lat1": 48.86471, "lon1": 2.23901, "lat2": 52.36760, "lon2": 4.90410, "meta": "par-ams"}

  print(f"{url}/api/price")
  print("POST body: ", payload)

  body = json.dumps(payload)

  headers = {"Content-type": "application/json"}

  r = await request(f"{url}/api", method="GET", headers=headers)
  print(f"GET request=> status:{r.status}, json:{await r.json()}")

  t = await request(f"{url}/api/price", body=body, method="POST", headers=headers)
  j = await t.json()
  print(f"GET request=> status:{t.status}, json:{j}")
  print(f"price = {j['price']} EUR  ({j['price_lo']}, {j['price_hi']})")

  document.getElementById("flight-info").innerText = \
  f"Price from API: {j['price']} EUR ({j['price_lo']}, {j['price_hi']})."

  print("lane_api")
