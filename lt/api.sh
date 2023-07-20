# api.sh for testing API service


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

 id="230801-001"
 da="23-08-01"
 
 laam=52.36760; loam=4.90410  # amsterdam
 lalo=51.50720; lolo=0.12760  # london
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

 dtemp='{"id":"%s", "da":"%s", "lat1":%s, "lon1":%s, "lat2":%s, "lon2":%s, "meta":"%s"}\n' # careful

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
 
#d1='{"id":"230701-001",                 "da":"23-07-01",                                          "lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'
#d2='{"id":"230701-001",        "co":100,"da":"23-07-01",                                          "lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'
#d3='{"id":"230701-001","seg":1,"co":100,"da":"23-07-01","ta":"10:00","db":"23-07-01","tb":"12:00","lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'

api_local() { 
 echo "test api functionality"
 echo "fn:"${FUNCNAME[*]}
 echo $(date)
 t0=$(date +%s)
 set -x # shell echo, set +x unsets
 
 #ia=$1; ib=$2 # select the test data range [d$ia, d$ib]
 ia=1; ib=8

 ci="api"     # image
 cn="$ci"_con # container name

 key="Api-Key: "`cat .key`
 ip="0.0.0.0"; p="3333"; url="http://$ip:$p"
 
 ct="Content-type: application/json"
 pp="json_pp" # prettyprinter

 # source api_data.sh # access weekly updated data

 docker stop $cn # clean
 docker rm   $cn
 docker rmi  $ci

 docker build -t $ci . -f Dockerfile."$ci" --force-rm=true 
 docker run -d -p $p:$p --name $cn $ci  # -d for detached mode in bg
 sleep 3

 curl -H "$key" -s "$url"     | "$pp" # request pp with silent -s
 curl -H "$key" -s "$url"/api | "$pp" 
 
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

 curl -H "$key" -s "$url"     | "$pp" 
 curl -H "$key" -s "$url"/api | "$pp" 

 for i in {1..7}
 do
   di="d$i"         # test selected
   d=$(echo ${!di}) # evaluated
   
   curl -s -X GET -H "$ct" -H "$key" $url/api/price --data "$d" | "$pp"
   curl -s -X GET -H "$ct" -H "$key" $url/api/eta   --data "$d" | "$pp" 
   curl -s -X GET -H "$ct" -H "$key" $url/api/co    --data "$d" | "$pp"
   curl -s -X GET -H "$ct" -H "$key" $url/api/route --data "$d" | "$pp"
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
 dc1='{"id":"230701-001",                 "da":"23-07-01",                                          "lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'
 dc2='{"id":"230701-001",        "co":100,"da":"23-07-01",                                          "lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'
 dc3='{"id":"230701-001","seg":1,"co":100,"da":"23-07-01","ta":"10:00","db":"23-07-01","tb":"12:00","lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'

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
 ds1='{"id":"230701-001",                 "da":"23-07-01",                                          "lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'
 ds2='{"id":"230701-001",        "co":100,"da":"23-07-01",                                          "lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'
 ds3='{"id":"230701-001","seg":1,"co":100,"da":"23-07-01","ta":"10:00","db":"23-07-01","tb":"12:00","lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'

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
 
 id="230701-001"
 da="23-07-01"
 lat1=60.19205
 lon1=24.94583
 lat2=60.10549
 lon2=24.15589
 template='{"id":"%s", "da":"%s", "lat1":%s, "lon1":%s, "lat2":%s, "lon2":%s}\n' # careful

 dr1=$(printf "$template" "$id" "$da" "$lat1" "$lon1" "$lat2" "$lon2")
 #dr1='{"id":"230701-001",                 "da":"23-07-01",                                          "lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'
 
 dr2='{"id":"230701-001",        "co":100,"da":"23-07-01",                                          "lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'
 dr3='{"id":"230701-001","seg":1,"co":100,"da":"23-07-01","ta":"10:00","db":"23-07-01","tb":"12:00","lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'

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

  id="230601-001"
  da="23-07-01"

  template='{"id":"%s", "da":"%s", "lat1":%s, "lon1":%s}\n'
  dr=$(printf "$template" "$id" "$da" "$lat1" "$lon1")
  echo $dr
}
