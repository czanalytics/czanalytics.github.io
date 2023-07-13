# api.sh for managing API service

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
d1='{"id":"230701-001",                 "da":"23-07-01",                                          "lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'
d2='{"id":"230701-001",        "co":100,"da":"23-07-01",                                          "lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'
d3='{"id":"230701-001","seg":1,"co":100,"da":"23-07-01","ta":"10:00","db":"23-07-01","tb":"12:00","lat1":60.19205,"lon1":24.94583,"lat2":60.10549,"lon2":24.15589}'
d4='{"id":"230702-001","seg":1,"co":100,"da":"23-07-02","ta":"10:00","db":"23-07-02","tb":"12:00","lat1":60.19205,"lon1":24.94583,"lat2":60.30549,"lon2":24.35589}'
d5='{"id":"230703-001","seg":1,"co":100,"da":"23-07-03","ta":"10:00","db":"23-07-03","tb":"12:00","lat1":60.19205,"lon1":24.94583,"lat2":60.50549,"lon2":24.55589}'
d6='{"id":"230703-001","seg":2,"co":100,"da":"23-07-03","ta":"15:00","db":"23-07-03","tb":"17:00","lat1":60.19205,"lon1":24.94583,"lat2":60.70549,"lon2":24.75589}'
d7='{"id":"230703-002","seg":1,"co":100,"da":"23-07-03","ta":"10:00","db":"23-07-03","tb":"12:00","lat1":60.19205,"lon1":24.94583,"lat2":60.90549,"lon2":24.95589}'

api_local() { 
 echo "test api functionality"
 echo "fn:"${FUNCNAME[*]}
 echo $(date)
 t0=$(date +%s)
 set -x # shell echo, set +x unsets

 ci="api"     # image
 cn="$ci"_con # container name
 ip="0.0.0.0"
 p="3333"
 
 url="http://$ip:$p"
 key="Api-Key: "`cat .secret_key`
 
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

 url=`cat .url`
 key="Api-Key: "`cat .secret_key`
 
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

 echo "TDB"
 
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

 echo "TDB"
 
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

 echo "TDB"
 
 set +x
 echo $(date)
 t1=$(date +%s)
 echo "time elapsed `expr $t1 - $t0` sec."
}
