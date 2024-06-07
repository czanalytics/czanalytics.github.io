# api.sh for managing API


api_clean() {
 echo "clean api container artifacts"
 echo "fn:"${FUNCNAME[*]}

 docker stop lane_api     # stop the container
 docker rm lane_api       # remove it
 docker rmi -f lane       # force image remove
 docker image prune -a    # prune all dangling images
}


api_data() {
 echo "prepare data for api container"
 echo "fn:"${FUNCNAME[*]}
 echo $(date)
 t0=$(date +%s)
 set -x

 echo "TDB"

 set +x
 echo $(date)
 t1=$(date +%s)
 echo "time elapsed `expr $t1 - $t0` sec."
}


api_model() {
 echo "prepare models for api container"
 echo "fn:"${FUNCNAME[*]}
 echo $(date)
 t0=$(date +%s)
 set -x

 echo "TDB"
 
 set +x
 echo $(date)
 t1=$(date +%s)
 echo "time elapsed `expr $t1 - $t0` sec."
}


# test payload 
# required: id, da, lat1, lon2, lat2, lon2, 
#                   (lat, lon) with 5 decimal provides ~1 meter accuracy
# optional: co for vehicle CO2 [g/km t], db for dat window, (ta,tb) for time window
# defaults: co=100, seg=1, (db,ta,tb)=(da,00:00,24:00)  

 id="231213-001"
 da="2023-12-13" 
 #da="23-12-13" # <=0.48

 laam=52.36760; loam=4.90410  # amsterdam
 lalo=51.50720; lolo=0.12760  # london ?NUTS-error?
 laco=55.67610; loco=12.56830 # copenhagen
 lapa=48.86471; lopa=2.23901  # paris
 lawa=52.23704; lowa=21.01753 # warsaw
 labe=52.52000; lobe=13.40495 # berlin
 last=59.33459; lost=18.06324 # stockholm
 lahe=60.19205; lohe=24.94583 # helsinki
 lata=59.43696; lota=23.75357 # tallinn
 lala=60.98267; lola=25.66121 # lahti
 laou=65.02154; loou=25.46988 # oulu

 mepawa="paris-warsaw"
 mepabe="paris-berlin"
 mebewa="berlin-warsaw"
 mehela="helsinki-lahti"
 meheou="helsinki-oulu"
 mehest="helsinki-stockholm"
 meheta="helsinki-tallinn"
 mehebe="helsinki-berlin"
 mecoam="copenhagen-amsterdam"
 mepalo="paris-london"
 mepaam="paris-amsterdam"

 dtemp='{"id":"%s", "da":"%s", "lat1":%s, "lon1":%s, "lat2":%s, "lon2":%s, "doc":"%s"}\n' # careful

 d1=$(printf  "$dtemp" "$id" "$da" "$lapa" "$lopa" "$lawa" "$lowa" "$mepawa")
 d2=$(printf  "$dtemp" "$id" "$da" "$lapa" "$lopa" "$labe" "$lobe" "$mepabe")
 d3=$(printf  "$dtemp" "$id" "$da" "$labe" "$lobe" "$lawa" "$lowa" "$mebewa")
 d4=$(printf  "$dtemp" "$id" "$da" "$lahe" "$lohe" "$lala" "$lola" "$mehela")
 d5=$(printf  "$dtemp" "$id" "$da" "$lahe" "$lohe" "$laou" "$loou" "$meheou")
 d6=$(printf  "$dtemp" "$id" "$da" "$lahe" "$lohe" "$last" "$lost" "$mehest")
 d7=$(printf  "$dtemp" "$id" "$da" "$lahe" "$lohe" "$lata" "$lota" "$meheta")
 d8=$(printf  "$dtemp" "$id" "$da" "$lahe" "$lohe" "$labe" "$lobe" "$mehebe")
 d9=$(printf  "$dtemp" "$id" "$da" "$laco" "$loco" "$laam" "$loam" "$mecoam")
 d10=$(printf "$dtemp" "$id" "$da" "$lapa" "$lopa" "$laam" "$loam" "$mepaam")
 #d11=$(printf "$dtemp" "$id" "$da" "$lapa" "$lopa" "$lalo" "$lolo" "$mepalo") # ERROR NUTS reqion not found??
 
#d1='{"id":"231201-001",                 "da":"2023-12-01",                                          "lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'
#d2='{"id":"231201-001",        "co":100,"da":"2023-12-01",                                          "lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'
#d3='{"id":"231201-001","seg":1,"co":100,"da":"2023-12-01","ta":"10:00","db":"2023-12-01","tb":"12:00","lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'


api_kb() { 
 echo "test KB API"
 echo "fn:"${FUNCNAME[*]}
 echo $(date)
 t0=$(date +%s)
 set -x # shell echo, set +x unsets

 ci="kb"     # image
 cn="$ci"_api  # container

 key="Api-Key: "`cat .key`
 ip="0.0.0.0"; p="3333"; url="http://$ip:$p"
 
 ct="Content-type: application/json"
 pp="json_pp" # prettyprinter

 docker stop $cn # clean
 docker rm   $cn
 docker rmi  $ci
 
 docker build -t $ci . -f Dockerfile."$ci" --force-rm=true 
 docker run -d -p $p:$p --name $cn $ci  # -d for detached mode in bg
 sleep 3

 curl -H "$key" -s "$url"     | "$pp" # silent -s
 curl -H "$key" -s "$url"/api | "$pp" 
 #curl -s -X GET -H "$ct" -H "$key" $url/api/dblist --data "$d" | "$pp"
 
 set +x
 docker logs -t $cn

 echo $(date)
 t1=$(date +%s)
 echo "time elapsed `expr $t1 - $t0` sec."
}


o1='{
 "order":   {"da": "2024-01-24", "id": "240124-0", "ta": "10:00", "tb": "12:00", "doc": "priority client"},
 "agents": [{"lat": 52.3676, "lon": 4.9041, "cap": 6, "id": 1, "doc": "a1ams"}, 
            {"lat": 45.764,  "lon": 4.8357, "cap": 3, "id": 2, "doc": "a2lyo"}],
 "picks":  [{"lat": 52.3676, "lon": 4.9041, "ids": [1, 2, 3, 4, 5], "ags": [1],    "doc": "amsterdam"},
            {"lat": 52.0907, "lon": 5.1214, "ids": [6, 7, 8],       "ags": [1],    "doc": "utrecht"}],
 "drops":  [{"lat": 45.764,  "lon": 4.8357, "ids": [1, 2, 3, 4],    "ags": [1, 2], "doc": "lyon"},
            {"lat": 44.9334, "lon": 4.8924, "ids": [5, 6],          "ags": [2],    "doc": "valence"},
            {"lat": 43.2965, "lon": 5.3698, "ids": [7, 8],          "ags": [2],    "doc": "marseille"}]}'
o2='{
 "order":   {"da": "2024-02-01", "id": "240201-0", "ta": "10:00", "tb": "12:00", "doc": "priority client"},
 "agents": [{"lat": 52.3676, "lon": 4.9041, "cap": 6, "id": 1, "doc": "a1ams"}, 
            {"lat": 45.764,  "lon": 4.8357, "cap": 3, "id": 2, "doc": "a2lyo"}],
 "picks":  [{"lat": 52.3676, "lon": 4.9041, "ids": [1, 2, 3, 4, 5], "ags": [1],    "doc": "amsterdam"},
            {"lat": 52.0907, "lon": 5.1214, "ids": [6, 7, 8],       "ags": [1],    "doc": "utrecht"}],
 "drops":  [{"lat": 45.764,  "lon": 4.8357, "ids": [1, 2, 3, 4],    "ags": [1, 2], "doc": "lyon"},
            {"lat": 44.9334, "lon": 4.8924, "ids": [5, 6],          "ags": [2],    "doc": "valence"},
            {"lat": 43.2965, "lon": 5.3698, "ids": [7, 8],          "ags": [2],    "doc": "marseille"}]}'

api_fuel() { 
 echo "test fuel info api"
 echo "fn:"${FUNCNAME[*]}
 echo $(date)
 t0=$(date +%s)
 set -x # shell echo, set +x unsets
 
 #ia=$1; ib=$2 # select the test data range [d$ia, d$ib]
 ia=1; ib=8

 ci="lane_fuel" # dev image
 cn="$ci"_api  # container name
 #ci="api"; cn="$ci"_con

 # key="Api-Key: "`cat .key` # optional
 #ip="0.0.0.0"; p="3333"; url="http://$ip:$p"
 ip="0.0.0.0"; p="7777"; url="http://$ip:$p" # unique dev port
 
 ct="Content-type: application/json"
 pp="json_pp" # prettyprinter

 # source api_data.sh # access weekly updated data

 docker stop $cn # clean
 docker rm   $cn
 docker rmi  $ci

 docker build -t $ci . -f Dockerfile.fuel --force-rm=true 
 #docker build -t $ci . -f Dockerfile."$ci" --force-rm=true 
 docker run -d -p $p:$p --name $cn $ci  # -d for detached mode in bg

 sleep 3

 curl -s "$url"     | "$pp" # request pp with silent -s
 #curl -H "$key" -s "$url"     | "$pp" # with optional key

 curl -s "$url"/api | "$pp" 
 
 of1='{"foo1": "bar1"}'
 of2='{"foo2": "bar2"}'
 
 for i in {1..2}
 do
   di="of$i"          # test selected
   d=$(echo ${!di}) # evaluated

   curl -s -X GET -H "$ct" $url/api/fuel --data "$d" | "$pp"
   
   #curl -s -X GET -H $ct" $url/api/fuel | "$pp"
   #curl -s -X POST -H "$ct" $url/api/fuel --data "$d" | "$pp"
 done

 set +x
 docker logs -t $cn

 echo $(date)
 t1=$(date +%s)
 echo "time elapsed `expr $t1 - $t0` sec."
}

# API schema for optimized bundling. v17
# Order. Execution date and time.
# Agents. Allocated vehicles for the delivery.
# Carrier: Additional info.
# GPS. Network node latitude & longitude and additional info.
# Lanes. Network graph, with arch attributes price/dist/eta/co2/risk.
# Scheduled. Timetable for regular train, ship, plane traffic.
# Timetable. Details of fixed schedules.
# Rules. Specific constraints.
# Optimize. Specifics of optimization goals.

bx='{
 "order":   {"da":"2024-02-05", "ta":"12:00", "tb":"15:00", 
             "id":"2024-02-05-001"},
 "agents": [{"location":"n1", "capacity":2, "id":"a1"},
            {"location":"n2", "capacity":3, "id":"a2"}],
 "cargo":  [{"pick": "n1", "drop":"n2", "id": "c1"},
            {"pick": "n1", "drop":"n2", "id": "c2"},
            {"pick": "n3", "drop":"n1", "id": "c3"},
            {"pick": "n2", "drop":"n5", "id": "c4"}],
 "lanes":  ["lane(n3,n1,40)","lane(n1,n3,40)",
            "lane(n3,n2,18)","lane(n2,n3,18)",
            "lane(n4,n1,36)","lane(n1,n4,36)",
	          "lane(n4,n3,37)","lane(n3,n4,37)",
            "lane(n5,n2,24)","lane(n2,n5,24)",
            "lane(n5,n3,26)","lane(n3,n5,26)"]
          }'

# changes: 
# 1) agent naming: a1 -> ag1
# 2) node name and distance: lane(n1,n3,40) -> lane(hub1,n3,30)
#                            {"pick":"n1" ...}  -> {"pick":"hub1" ...}  
# 3) new node next to n1: lane(depot0,hub1,1),lane(hub1,depot0,1)
# 4) relocate agent ag1: from n1 to depot0
# 5) capacity of ag2 from 3 to 1

b3='{
 "order":  {"id":"2024-06-06", "da":"2024-06-07", "ta":"09:00", "tb":"21:00"},

 "agent":[
   {"id":"ag01", "carrier":"cr01", "loc":"l01"},
   {"id":"ag02", "carrier":"cr02", "loc":"l01"},
   {"id":"ag03", "carrier":"cr03", "loc":"l01"}],

 "carrier":[
   {"id":"cr01", "type":"car_carrier", "l":12.0, "w":2.2, "h":3.5, "kg":12000, "name":"eurolohr_200", "url":"https://www.lohr.fr/catalogue/eurolohr-200/"},
   {"id":"cr02", "type":"car_carrier", "l":13.3, "w":2.2, "h":3.5, "kg":15000, "name":"eurolohr_300", "url":"https://www.lohr.fr/catalogue/eurolohr-300/"},
   {"id":"cr03", "type":"car_carrier", "l":25.3, "w":2.5, "h":4.0, "kg":20000, "name":"trsp_25"  , "url":"https://www.lohr.fr/catalogue/trsp-25-25/"}],

 "loc":[
   {"id":"l00", "lat":45.7640, "lon":4.8357, "type":"depot", "name":"lyon_depot"},
   {"id":"l01", "lat":48.8420, "lon":2.2489, "type":"depot", "name":"paris_depot"},
   {"id":"l11", "lat":48.8303, "lon":2.2964, "type":"capacity", "name":"paris_clio"},
   {"id":"l12", "lat":50.3369, "lon":3.2956, "type":"capacity", "name":"belgium_duster"},
   {"id":"l13", "lat":45.7623, "lon":4.6898, "type":"capacity", "name":"lyon_fiat"},
   {"id":"l14", "lat":52.0413, "lon":4.3517, "type":"capacity", "name":"hague_tesla"},
   {"id":"l20", "lat":45.6190, "lon":4.5350, "type":"demand", "name":"lyon_dealer"},
   {"id":"l21", "lat":49.5453, "lon":5.8190, "type":"demand", "name":"luxemburg_dealer"},
   {"id":"l22", "lat":52.3867, "lon":4.9226, "type":"demand", "name":"amsterdam_dealer"},
   {"id":"l23", "lat":52.0094, "lon":4.3116, "type":"demand", "name":"hague_dealer"},
   {"id":"l24", "lat":43.5591, "lon":3.8353, "type":"demand", "name":"lattes_dealer"},
   {"id":"l25", "lat":45.3194, "lon":4.8075, "type":"demand", "name":"chanas_dealer"},
   {"id":"l26", "lat":48.3334, "lon":4.0944, "type":"demand", "name":"lavau_dealer"},
   {"id":"l27", "lat":45.7858, "lon":3.1222, "type":"demand", "name":"clermont_ferrand_dealer"},
   {"id":"l28", "lat":42.6800, "lon":2.8109, "type":"demand", "name":"perpignan_dealer"},
   {"id":"l29", "lat":50.3872, "lon":3.5498, "type":"demand", "name":"saint_aulve_dealer"}],

 "item":[
   {"id":"i001", "l":4.1, "w":1.8, "h":1.5, "kg":995,  "name":"renault_clio"},
   {"id":"i002", "l":4.4, "w":1.9, "h":1.7, "kg":995,  "name":"dacia_duster"},
   {"id":"i003", "l":3.6, "w":1.7, "h":1.5, "kg":500,  "name":"fiat_500"},
   {"id":"i004", "l":5.1, "w":2.0, "h":1.7, "kg":2335, "name":"tesla_x"}],

 "cargo":  [
   {"id":"c201", "units": 5, "item":"i001", "pick":"l11", "drop":"l20"},
   {"id":"c202", "units": 5, "item":"i002", "pick":"l12", "drop":"l20"},
   {"id":"c203", "units":10, "item":"i003", "pick":"l13", "drop":"l20"},
   {"id":"c204", "units": 1, "item":"i004", "pick":"l14", "drop":"l20"},

   {"id":"c211", "units": 9, "item":"i001", "pick":"l11", "drop":"l21"},
   {"id":"c212", "units":10, "item":"i002", "pick":"l12", "drop":"l21"},
   {"id":"c213", "units": 7, "item":"i003", "pick":"l13", "drop":"l21"},
   {"id":"c214", "units": 3, "item":"i004", "pick":"l14", "drop":"l21"},
 
   {"id":"c221", "units": 5, "item":"i001", "pick":"l11", "drop":"l22"},
   {"id":"c222", "units":10, "item":"i002", "pick":"l12", "drop":"l22"},
   {"id":"c223", "units": 7, "item":"i003", "pick":"l13", "drop":"l22"},
   {"id":"c224", "units": 3, "item":"i004", "pick":"l14", "drop":"l22"},

   {"id":"c231", "units": 4, "item":"i001", "pick":"l11", "drop":"l23"},
   {"id":"c232", "units": 3, "item":"i002", "pick":"l12", "drop":"l23"},
   {"id":"c233", "units": 8, "item":"i003", "pick":"l13", "drop":"l23"},
   {"id":"c234", "units": 1, "item":"i004", "pick":"l14", "drop":"l23"},

   {"id":"c241", "units": 6, "item":"i001", "pick":"l11", "drop":"l24"},
   {"id":"c242", "units": 6, "item":"i002", "pick":"l12", "drop":"l24"},
   {"id":"c243", "units": 2, "item":"i003", "pick":"l13", "drop":"l24"},
   
   {"id":"c251", "units":11, "item":"i001", "pick":"l11", "drop":"l25"},
   {"id":"c252", "units": 4, "item":"i002", "pick":"l12", "drop":"l25"},
   {"id":"c253", "units": 8, "item":"i003", "pick":"l13", "drop":"l25"},
   {"id":"c254", "units": 2, "item":"i004", "pick":"l14", "drop":"l25"},
  
   {"id":"c261", "units": 9, "item":"i001", "pick":"l11", "drop":"l26"},
   {"id":"c262", "units": 8, "item":"i002", "pick":"l12", "drop":"l26"},
   {"id":"c263", "units": 8, "item":"i003", "pick":"l13", "drop":"l26"},
   {"id":"c264", "units": 3, "item":"i004", "pick":"l14", "drop":"l26"},
     
   {"id":"c271", "units":10, "item":"i001", "pick":"l11", "drop":"l27"},
   {"id":"c272", "units":10, "item":"i002", "pick":"l12", "drop":"l27"},
   {"id":"c273", "units": 7, "item":"i003", "pick":"l13", "drop":"l27"},
   {"id":"c274", "units": 3, "item":"i004", "pick":"l14", "drop":"l27"},
  
   {"id":"c281", "units": 9, "item":"i001", "pick":"l11", "drop":"l28"},
   {"id":"c282", "units":10, "item":"i002", "pick":"l12", "drop":"l28"},
   {"id":"c283", "units": 7, "item":"i003", "pick":"l13", "drop":"l28"},
   {"id":"c284", "units": 3, "item":"i004", "pick":"l14", "drop":"l28"},

   {"id":"c291", "units":10, "item":"i001", "pick":"l11", "drop":"l29"},
   {"id":"c292", "units": 9, "item":"i002", "pick":"l12", "drop":"l29"},
   {"id":"c293", "units":14, "item":"i003", "pick":"l13", "drop":"l29"},
   {"id":"c294", "units": 2, "item":"i004", "pick":"l14", "drop":"l29"}],

 "attribute":["dist", "cost", "risk"],
 
 "lane":[
   {"id":"l001", "a":"depot0", "b":"hub1", "attr":[3 ,     10,  0.0]},
   {"id":"l002", "a":"hub1",   "b":"n3",   "attr":[30,    100,  0.0]},
   {"id":"l003", "a":"n3",     "b":"n4",   "attr":[100,   200,  0.0]},
   {"id":"l004", "a":"n3",     "b":"n4",   "attr":[80,    200,  0.0]},
   {"id":"l005", "a":"n4",     "b":"n5",   "attr":[100,   300,  0.2]},
   {"id":"l006", "a":"n5",     "b":"n4",   "attr":[100,   300,  0.2]},
   {"id":"l007", "a":"hub1",   "b":"hub3", "attr":[1000, 1000,  0.0]}],

 "route":[".", "...", "..."],

 "timetable":[
   {"id":"tt1", "lane":"l003", "day":[6,7],       "dep":["13:00","18:00"], "arr":["15:00","21:00"], "mode":"truck", "url":""},
   {"id":"tt2", "lane":"l004", "day":[1,2,3,4,5], "dep":["06:00","10:00"], "arr":["07:00","11:10"], "mode":"rail",  "url":""},
   {"id":"tt3", "lane":"l005", "day":[1,2,3,4,5], "dep":["08:00","10:00"], "arr":["08:30","10:30"], "mode":"ferry", "url":""},
   {"id":"tt4", "lane":"l006", "day":[1,2,3,4,5], "dep":["09:00","12:00"], "arr":["09:30","12:30"], "mode":"ferry", "url":""},
   {"id":"tt5", "lane":"l007", "day":[1,3,5],     "dep":["13:00"],         "arr":["17:40"],         "mode":"air",   "url":""}],

 "rule":[
   {"id":"r001", "rule":"plan(Cost,ETA,CO), Cost < 1000"},
   {"id":"r003", "rule":"plan(Cost,ETA,CO), ETA < 10, CO < 10000"},
   {"id":"r004", "rule":"item(L,W,H,Weight), Weight < 2000"},
   {"id":"r005", "rule":"lane(risk) < 0.2"},
   {"id":"r006", "rule":"timetable(Lane,Departure,Arrival,ferry), Arrival < 17"},
   {"id":"r010", "rule":"carrier(Type,L,W,H), L < 15"}],

 "optimize":[
   {"id":"r01", "goal":"cost"},
   {"id":"r02", "goal":"time",           "rules":["r001"]},
   {"id":"r03", "goal":"resource-usage", "rules":["r008", "r009"]},
   {"id":"r04", "goal":"cost",                                  "routing":"ms"},
   {"id":"r05", "goal":"cost-and-risk",                         "routing":"google", "weather":"noaa"}]
}'

api_dev() { 
 echo "test bundle api extension"
 echo "fn:"${FUNCNAME[*]}
 echo $(date)
 t0=$(date +%s)
 set -x # shell echo, set +x unsets
 
 ia=1; ib=8

 ci="lane_dev" # image
 cn="$ci"_api  # container name

 #key="Api-Key: "`cat .key` # optional
 ip="0.0.0.0"; p="6666"; url="http://$ip:$p" # unique dev port
 
 ct="Content-type: application/json"
 pp="json_pp" # prettyprinter

 docker stop $cn # clean
 docker rm   $cn
 docker rmi  $ci

 docker build -t $ci . -f Dockerfile.bundle --force-rm=true 
 docker run -d -p $p:$p --name $cn $ci  # -d for detached mode in bg
 
 sleep 3

 curl -s "$url"     | "$pp" # request pp with silent -s
 curl -s "$url"/api | "$pp" 
 
 curl -s -X GET -H "$ct" $url/api/demo | "$pp"
 curl -s -X GET -H "$ct" $url/api/demodev | "$pp"

# for i in {3..3}
i=3 
#do
   di="b$i"         # test selected
   d=$(echo ${!di}) # evaluated

   curl -s -X GET  -H "$ct" $url/api/bundledev --data "$d" | "$pp"
# done

 set +x
 docker logs -t $cn

 echo $(date)
 t1=$(date +%s)
 echo "time elapsed `expr $t1 - $t0` sec."
}


# data for api_bundle()

b1='{
 "order":   {"da":"2024-02-05", "ta":"12:00", "tb":"15:00", 
             "id":"2024-02-05-001"},
 "agents": [{"location":"n1", "capacity":2, "id":"a1"},
            {"location":"n2", "capacity":3, "id":"a2"}],
 "cargo":  [{"pick": "n1", "drop":"n2", "id": "c1"},
            {"pick": "n1", "drop":"n2", "id": "c2"},
            {"pick": "n3", "drop":"n1", "id": "c3"},
            {"pick": "n2", "drop":"n5", "id": "c4"}],
 "lanes":  ["lane(n3,n1,40)","lane(n1,n3,40)",
            "lane(n3,n2,18)","lane(n2,n3,18)",
            "lane(n4,n1,36)","lane(n1,n4,36)",
	          "lane(n4,n3,37)","lane(n3,n4,37)",
            "lane(n5,n2,24)","lane(n2,n5,24)",
            "lane(n5,n3,26)","lane(n3,n5,26)"]
          }'

# changes: 
# 1) agent naming: a1 -> ag1
# 2) node name and distance: lane(n1,n3,40) -> lane(hub1,n3,30)
#                            {"pick":"n1" ...}  -> {"pick":"hub1" ...}  
# 3) new node next to n1: lane(depot0,hub1,1),lane(hub1,depot0,1)
# 4) relocate agent ag1: from n1 to depot0
# 5) capacity of ag2 from 3 to 1

b2='{
 "order":   {"da":"2024-02-06", "ta":"12:00", "tb":"16:00", 
             "id":"2024-02-06-001"},
 "agents": [{"location":"depot0", "capacity":2, "id":"ag1"},
            {"location":"n2", "capacity":1, "id":"ag2"}],
 "cargo":  [{"pick": "hub1", "drop":"n2", "id": "c1"},
            {"pick": "hub1", "drop":"n2", "id": "c2"},
            {"pick": "n3", "drop":"hub1", "id": "c3"},
            {"pick": "n2", "drop":"n5", "id": "c4"}],
 "lanes":  ["lane(depot0,hub1,3)","lane(hub1,depot0,3)",
            "lane(n3,hub1,30)","lane(hub1,n3,30)",
            "lane(n3,n2,18)","lane(n2,n3,18)",
            "lane(n4,hub1,36)","lane(hub1,n4,36)",
	          "lane(n4,n3,37)","lane(n3,n4,37)",
            "lane(n5,n2,24)","lane(n2,n5,24)",
            "lane(n5,n3,26)","lane(n3,n5,26)"]
          }'

api_bundle() { 
 echo "test bundle api"
 echo "fn:"${FUNCNAME[*]}
 echo $(date)
 t0=$(date +%s)
 set -x # shell echo, set +x unsets
 
 #ia=$1; ib=$2 # select the test data range [d$ia, d$ib]
 ia=1; ib=8

 ci="lane_bundle" # image
 cn="$ci"_api  # container name
 #ci="api"; cn="$ci"_con

 #key="Api-Key: "`cat .key` # optional
 ip="0.0.0.0"; p="6666"; url="http://$ip:$p" # unique dev port
 
 ct="Content-type: application/json"
 pp="json_pp" # prettyprinter

 # source api_data.sh # access weekly updated data

 docker stop $cn # clean
 docker rm   $cn
 docker rmi  $ci

 docker build -t $ci . -f Dockerfile.bundle --force-rm=true 
 docker run -d -p $p:$p --name $cn $ci  # -d for detached mode in bg
 
 sleep 3

 curl -s "$url"     | "$pp" # request pp with silent -s
 curl -s "$url"/api | "$pp" 
 #curl -H "$key" -s "$url"     | "$pp" # with optional key
 #curl -H "$key" -s "$url"/api | "$pp" 
 
 curl -s -X GET -H "$ct" $url/api/demo | "$pp"

 for i in {1..2}
 do
   di="b$i"         # test selected
   d=$(echo ${!di}) # evaluated

   curl -s -X GET  -H "$ct" $url/api/bundle --data "$d" | "$pp"
   #curl -s -X POST -H "$ct" $url/api/bundle --data "$d" | "$pp"

   #curl -s -X GET -H "$ct" $url/api/demo --data "$o1" | "$pp"
   #curl -s -X POST -H "$ct" $url/api/demo --data "$o2" | "$pp"
 done

 set +x
 docker logs -t $cn

 echo $(date)
 t1=$(date +%s)
 echo "time elapsed `expr $t1 - $t0` sec."
}

api_local() { 
 echo "test api functionality"
 echo "fn:"${FUNCNAME[*]}
 echo $(date)
 t0=$(date +%s)
 set -x # shell echo, set +x unsets
 
 #ia=$1; ib=$2 # select the test data range [d$ia, d$ib]
 ia=1; ib=8

 ci="lane_dev" # dev image
 cn="$ci"_api  # container name
 #ci="api"; cn="$ci"_con

 key="Api-Key: "`cat .key`
 #ip="0.0.0.0"; p="3333"; url="http://$ip:$p"
 ip="0.0.0.0"; p="8888"; url="http://$ip:$p" # unique dev port
 
 ct="Content-type: application/json"
 pp="json_pp" # prettyprinter

 # source api_data.sh # access weekly updated data

 docker stop $cn # clean
 docker rm   $cn
 docker rmi  $ci

 docker build -t $ci . -f Dockerfile.api --force-rm=true 
 #docker build -t $ci . -f Dockerfile."$ci" --force-rm=true 
 docker run -d -p $p:$p --name $cn $ci  # -d for detached mode in bg
 
 sleep 3

 #curl -H "$key" -s "$url"     | "$pp" # request pp with silent -s
 #curl -H "$key" -s "$url"/api | "$pp" 
 
 for i in {1..10}
 do
   di="d$i"         # test selected
   d=$(echo ${!di}) # evaluated

   curl -s -X GET -H "$ct" -H "$key" $url/api/price --data "$d" | "$pp"
   curl -s -X GET -H "$ct" -H "$key" $url/api/eta   --data "$d" | "$pp" 
   curl -s -X GET -H "$ct" -H "$key" $url/api/co    --data "$d" | "$pp"
   curl -s -X GET -H "$ct" -H "$key" $url/api/route --data "$d" | "$pp"
 done

 set +x
 docker logs -t $cn

 echo $(date)
 t1=$(date +%s)
 echo "time elapsed `expr $t1 - $t0` sec."
}


api_docker_hub() {
 echo "push the image to docker hub"
 echo "fn:"${FUNCNAME[*]}
 echo $(date)
 t0=$(date +%s)
 week=$(date +%V)
 set -x

 docker buildx build --no-cache -f Dockerfile.api --platform=linux/amd64,linux/arm64/v8 -t czanalytics/lane:v0.$week --push .
 
 # docker buildx create --name multiarch --driver docker-container --use 
 # docker buildx build --no-cache -f Dockerfile.api --platform=linux/amd64,linux/arm64/v8,linux/arm/v7 -t czanalytics/lane:latest --push .
 
 #docker tag lane_dev czanalytics/lane:v0.$week
 #docker push czanalytics/lane:v0.$week

 # pulling
 #docker run -dp 127.0.0.1:8888:8888 czanalytics/lane:v0.$week

 set +x
 echo $(date)
 t1=$(date +%s)
 echo "time elapsed `expr $t1 - $t0` sec."
}


api_deploy() {
 echo "deploy api container"
 echo "fn:"${FUNCNAME[*]}
 echo $(date)
 t0=$(date +%s)
 set -x

 echo "TDB"
 
 set +x
 echo $(date)
 t1=$(date +%s)
 echo "time elapsed `expr $t1 - $t0` sec."
}

o0='{"agents": [{"lat": 1, "lon": 2}, {"lat":3, "lon":4}],
"drops": [{"x":1, "y":3, "z": [1,2,3]}]}'

o2='{"agents": [{"lat": 52.3676, "lon": 4.9041, "cap": 6, "id": 1, "doc": "a1ams"}, 
                {"lat": 45.764, "lon": 4.8357, "cap": 3, "id": 2, "doc": "a2lyo"}]}'

api_cloud() {
 echo "test the deployed api"
 echo "fn:"${FUNCNAME[*]}
 echo $(date)
 t0=$(date +%s)
 set -x

 url=`cat .url_api`
 key="Api-Key: "`cat .key`
 
 ct="Content-type: application/json"
 pp="json_pp"

 #curl -H "$key" -s "$url"     | "$pp" 
 #curl -H "$key" -s "$url"/api | "$pp" 

 #curl -s -X GET -H "$ct" $url/api/routing --data "$o1" | "$pp" 
 #curl -s -X POST -H "$ct" $url/api/routing --data "$o1" | "$pp"
 
 for i in {1..1}
 do
   di="d$i"         # test selected
   d=$(echo ${!di}) # evaluated
   
   curl -s -X GET -H "$ct" $url/api/price --data "$d" | "$pp"
   curl -s -X GET -H "$ct" $url/api/eta   --data "$d" | "$pp" 
   curl -s -X GET -H "$ct" $url/api/co    --data "$d" | "$pp"
 done


 for i in {1..2}
 do
   di="d$i"         # test selected
   d=$(echo ${!di}) # evaluated
   
   curl -s -X POST -H "$ct" $url/api/price --data "$d" | "$pp"
   curl -s -X POST -H "$ct" $url/api/eta   --data "$d" | "$pp" 
   curl -s -X POST -H "$ct" $url/api/co    --data "$d" | "$pp"
 done

 set +x
 echo $(date)
 t1=$(date +%s)
 echo "time elapsed `expr $t1 - $t0` sec."
}


api_route() {
 echo "Route between two locations"
 echo "fn:"${FUNCNAME[*]}
 echo $(date)
 t0=$(date +%s)
 set -x
 
 key="Api-Key: "`cat .key`
 ip="0.0.0.0"; p="3333"; url="http://$ip:$p"

 ct="Content-type: application/json"
 pp="json_pp"
 
 id="231201-001"
 da="2023-12-01"
 lat1=60.19205
 lon1=24.94583
 lat2=60.10549
 lon2=24.15589
 template='{"id":"%s", "da":"%s", "lat1":%s, "lon1":%s, "lat2":%s, "lon2":%s}\n' # careful

 dr1=$(printf "$template" "$id" "$da" "$lat1" "$lon1" "$lat2" "$lon2")
 dr2=$d2 # testing price-calculator payload 

 curl -H "$key" -s "$url"/api/route | "$pp" 

 for i in {1..2}
 do
   di="dr$i"        # test selected
   d=$(echo ${!di}) # evaluated
   
   curl -s -X GET -H "$ct" -H "$key" $url/api/route --data "$d" | "$pp"
 done

 set +x
 echo $(date)
 t1=$(date +%s)
 echo "time elapsed `expr $t1 - $t0` sec."
}


# routing conf. for numbered units: 
# {
#  'order': {'id': '231224-0', 'da': '2023-12-26'}, 
#  'picks': [(52.3676, 4.9041, [1, 2, 3, 4, 5], 'amsterdam'), 
#            (52.0907, 5.1214, [6, 7, 8]), 'utrecht'], 
#  'drops': [(45.764 , 4.8357, [1, 2, 3, 4], 'lyon'), 
#            (44.9334, 4.8924, [5, 6], 'valence'), (
#             43.2965, 5.3698, [7, 8], 'marseille')], 
#  'agents': [(52.3676, 4.9041, 6, 'amsterdam', 'ag1', 'greedy'), 
#             (45.764 , 4.8357, 3, 'lyon', 'ag2', 'force')]
# }
#
api_routing() {
 echo "Routing for cargo (pick, drop) -network."
 echo "fn:"${FUNCNAME[*]}
 echo $(date)
 t0=$(date +%s)
 set -x
 
 key="Api-Key: "`cat .key`
 ip="0.0.0.0"; p="3333"; url="http://$ip:$p"

 ct="Content-type: application/json"
 pp="json_pp"

 # routing network
 
 id="231201-001"
 da="2023-07-01"
 lat1=60.19205
 lon1=24.94583
 lat2=60.10549
 lon2=24.15589
 template='{"id":"%s", "da":"%s", "lat1":%s, "lon1":%s, "lat2":%s, "lon2":%s}\n' # careful

 dr1=$(printf "$template" "$id" "$da" "$lat1" "$lon1" "$lat2" "$lon2")
 dr2=$d2 # testing price-calculator payload 

 #curl -H "$key" -s "$url"/api/routing | "$pp" 

 for i in {1..2}
 do
   di="dr$i"        # test selected
   d=$(echo ${!di}) # evaluated
   
    curl -s -X POST -H "$ct" $url/api/routing --data "$o1" | "$pp"
    curl -s -X GET  -H "$ct" $url/api/routing --data "$o1" | "$pp"
   #curl -s -X POST -H "$ct" $url/api/routing --data "$d" | "$pp"
   #curl -s -X GET -H "$ct" -H "$key" $url/api/routing --data "$d" | "$pp"
 done

 set +x
 echo $(date)
 t1=$(date +%s)
 echo "time elapsed `expr $t1 - $t0` sec."
}


api_config() {
 echo "configure the api service"
 echo "fn:"${FUNCNAME[*]}
 echo $(date)
 t0=$(date +%s)
 set -x

 key="Api-Key: "`cat .key_conf` # notice unique key
 ip="0.0.0.0"; p="3333"; url="http://$ip:$p"

 ct="Content-type: application/json"
 pp="json_pp"

 # data config
 dc1='{"id":"231201-001",                 "da":"2023-07-01",                                          "lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'
 dc2='{"id":"231201-001",        "co":100,"da":"2023-07-01",                                          "lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'
 dc3='{"id":"231201-001","seg":1,"co":100,"da":"2023-07-01","ta":"10:00","db":"2023-07-01","tb":"12:00","lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'

 curl -H "$key" -s "$url"/api/config | "$pp" 

 for i in {1..2}
 do
   di="dc$i"        # test selected
   d=$(echo ${!di}) # evaluated
   
   curl -s -X GET -H "$ct" -H "$key" $url/api/config --data "$d" | "$pp"
 done
 
 set +x
 echo $(date)
 t1=$(date +%s)
 echo "time elapsed `expr $t1 - $t0` sec."
}


api_status() {
 echo "inspect the status of api service"
 echo "fn:"${FUNCNAME[*]}
 echo $(date)
 t0=$(date +%s)
 set -x

 key="Api-Key: "`cat .key`
 ip="0.0.0.0"; p="3333"; url="http://$ip:$p"

 ct="Content-type: application/json"
 pp="json_pp"

 # data status
 ds1='{"id":"231201-001",                 "da":"2023-12-01",                                          "lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'
 ds2='{"id":"231201-001",        "co":100,"da":"2023-12-01",                                          "lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'
 ds3='{"id":"231201-001","seg":1,"co":100,"da":"2023-12-01","ta":"10:00","db":"2023-07-01","tb":"12:00","lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'

 curl -H "$key" -s "$url"/api/status | "$pp" 

 for i in {1..2}
 do
   di="ds$i"        # test selected
   d=$(echo ${!di}) # evaluated
   
   curl -s -X GET -H "$ct" -H "$key" $url/api/status --data "$d" | "$pp"
 done

 set +x
 echo $(date)
 t1=$(date +%s)
 echo "time elapsed `expr $t1 - $t0` sec."
}


api_report() {
 echo "prepare service reports"
 echo "fn:"${FUNCNAME[*]}
 echo $(date)
 t0=$(date +%s)
 set -x
 
 key="Api-Key: "`cat .key`
 ip="0.0.0.0"; p="3333"; url="http://$ip:$p"

 ct="Content-type: application/json"
 pp="json_pp"

 # data report
 
 id="231201-001"
 da="2023-12-01"
 lat1=60.19205
 lon1=24.94583
 lat2=60.10549
 lon2=24.15589
 template='{"id":"%s", "da":"%s", "lat1":%s, "lon1":%s, "lat2":%s, "lon2":%s}\n' # careful

 dr1=$(printf "$template" "$id" "$da" "$lat1" "$lon1" "$lat2" "$lon2")
 #dr1='{"id":"231201-001",                 "da":"2023-12-01",                                          "lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'
 
 dr2='{"id":"231201-001",        "co":100,"da":"2023-12-01",                                          "lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'
 dr3='{"id":"231201-001","seg":1,"co":100,"da":"2023-12-01","ta":"10:00","db":"2023-07-01","tb":"12:00","lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'

 curl -H "$key" -s "$url"/api/report | "$pp" 

 for i in {1..2}
 do
   di="dr$i"        # test selected
   d=$(echo ${!di}) # evaluated
   
   curl -s -X GET -H "$ct" -H "$key" $url/api/report --data "$d" | "$pp"
 done

 set +x
 echo $(date)
 t1=$(date +%s)
 echo "time elapsed `expr $t1 - $t0` sec."
}

# usage: source api.sh && loc_dict 1.1 1.2 2.2 2.3
loc_dict() {
  echo "testing dictionary and fn anguments"
  
  echo "lat1 $1 lon1 $2 lat2 $3 lon2 $4"

  declare -A co=(
    [name]="Acme Corp."
    [loc]="New York City, NY"
    [lat]=$1
    [lon]=$2
    [industry]="Finance"
    [size]="Large"
    [founded]="1920"
  )

  printf "Company details:\n"
  for key in "${!co[@]}"; do
    printf "%s: %s\n" "$key" "${co[$key]}"
  done

  co["loc"]="Los Angeles, CA"

  printf "\nUpdated details:\n"
  for key in "${!co[@]}"; do
    printf "%s: %s\n" "$key" "${co[$key]}"
  done

  key=lat
  echo "${co[$key]}"
  echo "${co['lat']}"
  echo "${co['lon']}"
  lat1=${co['lat']}
  lon1=${co['lon']}
  echo $lat1

  id="231201-001"
  da="2023-12-10"

  template='{"id":"%s", "da":"%s", "lat1":%s, "lon1":%s}\n'
  dr=$(printf "$template" "$id" "$da" "$lat1" "$lon1")
  echo $dr
}
