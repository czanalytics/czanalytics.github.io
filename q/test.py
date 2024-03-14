# test.py is python version of api.sh
# Usage: first lauch the API server, see api.sh 
#        then run $make test, see Makefile

import pandas as pd
import numpy as np
import json # built-in module, no need to install
import requests # https://requests.readthedocs.io/en/latest/user/quickstart/

#import pytest # https://flask.palletsprojects.com/en/2.3.x/testing/

# ci="api"     # image
# cn="$ci"_con # container name

ip = "0.0.0.0"
p = "3333"
url = "http://" + ip + ":" + p
ct = {'Content-type': 'application/json'}

# pp="json_pp" # prettyprinter

# test payload 
# required: id, da, lat1, lon2, lat2, lon2, 
#                   (lat, lon) with 5 decimals, or ~1 meter accuracy
# defaults: co=100, seg=1, (db,ta,tb)=(da,00:00,24:00)  

# test data
dt = pd.DataFrame(np.array([
    ["helsinki",     60.19205,   24.94583],
    ["lahti",        60.98267,   25.66121],
    ['oulu',         65.02154,   25.46988],
    ["tallinn",      59.43696,   23.75357],
    ['stockholm',    59.33459,   18.06324],
    ['warsaw',       52.23704,   21.01753],
    ['paris',        48.86471,    2.34901],
    ['berlin',       52.52000,   13.40495]]),
    columns=['town', 'lat', 'lon'])

dt['town'] = dt['town'].astype('string') # types
dt['lat'] = dt['lat'].astype('float')
dt['lon'] = dt['lon'].astype('float')

dt, dt.info() # final

lat1 = dt[dt['town']=='paris']['lat'].values[0]
lon1 = dt[dt['town']=='paris']['lon'].values[0]

lat2 = dt[dt['town']=='warsaw']['lat'].values[0]
lon2 = dt[dt['town']=='warsaw']['lon'].values[0]


d0 = {"id":"231210-001",                 "da":"2023-10-10",                                          "lat1":lat1,    "lon1":lon1,    "lat2":lat2,    "lon2":lon2}

d1 = {"id":"231201-001",                 "da":"2023-12-01",                                          "lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}
d2 = {"id":"231201-001",        "co":100,"da":"2023-12-01",                                          "lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}
d3 = {"id":"231201-001","seg":1,"co":100,"da":"2023-12-01","ta":"10:00","db":"2023-12-01","tb":"12:00","lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}
d4 = {"id":"231202-001","seg":1,"co":100,"da":"2023-12-02","ta":"10:00","db":"2023-12-02","tb":"12:00","lat1":60.19205,"lon1":24.94583,"lat2":60.30549,"lon2":24.35589}
d5 = {"id":"231203-001","seg":1,"co":100,"da":"2023-12-03","ta":"10:00","db":"2023-12-03","tb":"12:00","lat1":60.19205,"lon1":24.94583,"lat2":60.50549,"lon2":24.55589}
d6 = {"id":"231203-001","seg":2,"co":100,"da":"2023-12-03","ta":"15:00","db":"2023-12-03","tb":"17:00","lat1":60.19205,"lon1":24.94583,"lat2":60.70549,"lon2":24.75589}
d7 = {"id":"231203-002","seg":1,"co":100,"da":"2023-12-03","ta":"10:00","db":"2023-12-03","tb":"12:00","lat1":60.19205,"lon1":24.94583,"lat2":60.90549,"lon2":24.95589}

# source api_data.sh # access weekly updated data

# docker stop $cn # clean
# docker rm   $cn
# docker rmi  $ci

# docker build -t $ci . -f Dockerfile."$ci" --force-rm=true 
# docker run -d -p $p:$p --name $cn $ci  # -d for detached mode in bg
# sleep 3

# curl -s "$url"/api | "$pp" # request pp with silent -s

r = requests.get(url + '/api')

print(r.json())

#print(r.text)
# for i in {1..7}
#   di="d$i"         # test selected
#   d=$(echo ${!di}) # evaluated
# print(d1)

d = d0
#d = d1

rp = requests.get(url + '/api/price',   headers=ct, data=json.dumps(d))
re = requests.get(url + '/api/eta',     headers=ct, data=json.dumps(d))
rc = requests.get(url + '/api/co',      headers=ct, data=json.dumps(d))
rr = requests.get(url + '/api/route',   headers=ct, data=json.dumps(d))
ro = requests.get(url + '/api/routing', headers=ct, data=json.dumps(d))

print(rp.json())
print(re.json())
print(rc.json())
print(rr.json())

rpj = json.dumps(rp.json(), indent=3)
print(rpj)

rej = json.dumps(re.json(), indent=3)
print(rej)

#print(rp.headers); print(rp.text)
#dp = json.loads(rp.content); print(dp)
#   curl -s -X GET -H "$ct" $url/api/price --data "$d" | "$pp"
# docker logs -t $cn

# example 1 PROTO
# api/routing paylaod
# NOTE that instead of town name we will use lat & lon values
routing1 = {"picks": [["amsterdam", 5], ["utrecht", 3]],
            "drops": [["lyon", 4], ["valence", 2], ["marseille", 2]],
            "agents": [["amsterdam", 6, "ag1", "greedy"]]}

# example 2
# NOTE agent capacity, name and strategy configures
routing2 = {"picks": [["groningen", 2], ["utrecht", 2], ["hoofddorp", 4]],
            "drops": [["amsterdam", 4], ["amstelveen", 3], ["hague", 1]],
            "agents": [["amsterdam", 12, "ag3", "step1"]]}

# Multiple agents with different homebases and strategies
routing3 = {"picks": [["groningen", 2], ["utrecht", 2], ["hoofddorp", 4]],
            "drops": [["amsterdam", 4], ["amstelveen", 3], ["hague", 1]],
            "agents": [["amsterdam", 12, "ag3", "step1"], ["hague", 6, "ag4", "ai"]]}

# routing1 output
# - each pick and drop action takes 0.1 hours
# - pu and du are remaining units to be picked and dropped
#
#     id     t agent     act  u   location  pu  du  policy  umax       home
# 0    1   0.0   ag1  policy  0  amsterdam   8   8  greedy     6  amsterdam
# 1    1   0.5   ag1    pick  5  amsterdam   3   8  greedy     6  amsterdam
# 2    1  12.7   ag1    move  5       lyon   3   8  greedy     6  amsterdam
# 3    1  13.1   ag1    drop  1       lyon   3   4  greedy     6  amsterdam
# 4    1  25.0   ag1    move  1    utrecht   3   4  greedy     6  amsterdam
# 5    1  25.3   ag1    pick  4    utrecht   0   4  greedy     6  amsterdam
# 6    1  37.2   ag1    move  4    valence   0   4  greedy     6  amsterdam
# 7    1  37.4   ag1    drop  2    valence   0   2  greedy     6  amsterdam
# 8    1  42.3   ag1    move  2  marseille   0   2  greedy     6  amsterdam
# 9    1  42.5   ag1    drop  0  marseille   0   0  greedy     6  amsterdam
# 10   1  58.0   ag1    home  0  amsterdam   0   0  greedy     6  amsterdam

# routing2
#
#     id     t agent     act  u    location  pu  du policy  umax       home
# 0    1   0.0   ag3  policy  0   amsterdam   8   8  step1    12  amsterdam
# 1    1   1.0   ag3    move  0   hoofddorp   8   8  step1    12  amsterdam
# 2    1   1.4   ag3    pick  4   hoofddorp   4   8  step1    12  amsterdam
# 3    1   2.4   ag3    move  4   amsterdam   4   8  step1    12  amsterdam
# 4    1   2.8   ag3    drop  0   amsterdam   4   4  step1    12  amsterdam
# 5    1   3.8   ag3    move  0  amstelveen   4   4  step1    12  amsterdam
# 6    1   6.6   ag3    move  0   groningen   4   4  step1    12  amsterdam
# 7    1   6.8   ag3    pick  2   groningen   2   4  step1    12  amsterdam
# 8    1   9.6   ag3    move  2  amstelveen   2   4  step1    12  amsterdam
# 9    1   9.8   ag3    drop  0  amstelveen   2   2  step1    12  amsterdam
# 10   1  11.1   ag3    move  0     utrecht   2   2  step1    12  amsterdam
# 11   1  11.3   ag3    pick  2     utrecht   0   2  step1    12  amsterdam
# 12   1  12.6   ag3    move  2  amstelveen   0   2  step1    12  amsterdam
# 13   1  12.7   ag3    drop  1  amstelveen   0   1  step1    12  amsterdam
# 14   1  14.2   ag3    move  1       hague   0   1  step1    12  amsterdam
# 15   1  14.3   ag3    drop  0       hague   0   0  step1    12  amsterdam

