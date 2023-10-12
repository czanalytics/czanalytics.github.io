# mt.py

import json

from pyodide.http import pyfetch

url = "https://violet-valleys.runblade.host"

import pandas as pd

from pyodide.http import open_url

import js
from js import document
from pyodide.ffi import create_proxy

async def mt_api(*args, **kwargs):
  #print("mt_api ...")

  payload = {"text": "Hej", "to": "fi"}
  print(f"{url}/api/mt/q=", payload)

  body = json.dumps(payload)

  headers = {"Content-type": "application/json"}

  #r = await request(f"{url}/api", method="GET", headers=headers)
  #print(f"GET request=> status:{r.status}, json:{await r.json()}")


  document.getElementById("out").innerText = f"Hei"

  #print("mt_api done")

