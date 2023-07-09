# test.py is python version of api.sh
# Usage: first lauch the API server, see api.sh 
#        then run $make test, see Makefile

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


d1 = {"id":"230701-001",                 "da":"23-07-01",                                          "lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}
d2 = {"id":"230701-001",        "co":100,"da":"23-07-01",                                          "lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}
d3 = {"id":"230701-001","seg":1,"co":100,"da":"23-07-01","ta":"10:00","db":"23-07-01","tb":"12:00","lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}
d4 = {"id":"230702-001","seg":1,"co":100,"da":"23-07-02","ta":"10:00","db":"23-07-02","tb":"12:00","lat1":60.19205,"lon1":24.94583,"lat2":60.30549,"lon2":24.35589}
d5 = {"id":"230703-001","seg":1,"co":100,"da":"23-07-03","ta":"10:00","db":"23-07-03","tb":"12:00","lat1":60.19205,"lon1":24.94583,"lat2":60.50549,"lon2":24.55589}
d6 = {"id":"230703-001","seg":2,"co":100,"da":"23-07-03","ta":"15:00","db":"23-07-03","tb":"17:00","lat1":60.19205,"lon1":24.94583,"lat2":60.70549,"lon2":24.75589}
d7 = {"id":"230703-002","seg":1,"co":100,"da":"23-07-03","ta":"10:00","db":"23-07-03","tb":"12:00","lat1":60.19205,"lon1":24.94583,"lat2":60.90549,"lon2":24.95589}

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

rp = requests.get(url + '/api/price', headers=ct, data=json.dumps(d1))
re = requests.get(url + '/api/eta',   headers=ct, data=json.dumps(d1))
rc = requests.get(url + '/api/co',    headers=ct, data=json.dumps(d1))
rr = requests.get(url + '/api/route', headers=ct, data=json.dumps(d1))

print(rp.json())
print(re.json())
print(rc.json())
print(rr.json())

#print(rp.headers); print(rp.text)
#dp = json.loads(rp.content); print(dp)
#   curl -s -X GET -H "$ct" $url/api/price --data "$d" | "$pp"
# docker logs -t $cn

