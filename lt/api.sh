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

o1='{
 "order":   {"da": "2023-12-23", "id": "231223-0", "ta": "10:00", "tb": "12:00", "doc": "priority client"},
 "agents": [{"lat": 52.3676, "lon": 4.9041, "cap": 6, "id": 1, "doc": "a1ams"}, 
            {"lat": 45.764,  "lon": 4.8357, "cap": 3, "id": 2, "doc": "a2lyo"}],
 "picks":  [{"lat": 52.3676, "lon": 4.9041, "ids": [1, 2, 3, 4, 5], "ags": [1],    "doc": "amsterdam"},
            {"lat": 52.0907, "lon": 5.1214, "ids": [6, 7, 8],       "ags": [1],    "doc": "utrecht"}],
 "drops":  [{"lat": 45.764,  "lon": 4.8357, "ids": [1, 2, 3, 4],    "ags": [1, 2], "doc": "lyon"},
            {"lat": 44.9334, "lon": 4.8924, "ids": [5, 6],          "ags": [2],    "doc": "valence"},
            {"lat": 43.2965, "lon": 5.3698, "ids": [7, 8],          "ags": [2],    "doc": "marseille"}]}'

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
