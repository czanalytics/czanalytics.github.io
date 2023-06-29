# api.sh
# usage: source api.sh && api 2>&1 | tee tmp.txt 
api() { 
 # test api functionality
 echo "fn:"${FUNCNAME[*]}
 echo $(date)
 t0=$(date +%s)
 set -x # shell echo, set +x unsets

 ci="api"     # image
 cn="$c"_con  # container name
 ip="0.0.0.0"
 p="3333"
 url="http://$ip:$p"
 pp="json_pp" # prettyprinting
 ct="Content-type: application/json"
 
 # test payloads
 d1='{"id":"230701-001","seg":1,"da":"23-07-01","ta":"10:00","db":"23-07-01","tb":"12:00","lat1":60.192059,"lon1":24.945831,"lat2":60.105490,"lon2":24.155899}'
 d2='{"id":"230702-001","seg":1,"da":"23-07-02","ta":"10:00","db":"23-07-02","tb":"12:00","lat1":60.192059,"lon1":24.945831,"lat2":60.305490,"lon2":24.355899}'
 d3='{"id":"230703-001","seg":1,"da":"23-07-03","ta":"10:00","db":"23-07-03","tb":"12:00","lat1":60.192059,"lon1":24.945831,"lat2":60.505490,"lon2":24.555899}'
 d4='{"id":"230703-001","seg":2,"da":"23-07-03","ta":"15:00","db":"23-07-03","tb":"17:00","lat1":60.192059,"lon1":24.945831,"lat2":60.705490,"lon2":24.755899}'
 d5='{"id":"230703-002","seg":1,"da":"23-07-03","ta":"10:00","db":"23-07-03","tb":"12:00","lat1":60.192059,"lon1":24.945831,"lat2":60.905490,"lon2":24.955899}'
 
 docker stop $cn # clean
 docker rm   $cn
 docker rmi  $ci

 docker build -t $ci . -f Dockerfile."$ci" --force-rm=true 
 docker run -d -p $p:$p --name $cn $ci  # -d for detached mode in bg
 
 sleep 3

 curl -s "$url"/api | "$pp" # request pp with silent -s

 for i in {1..5}
 do
   di="d$i"         # test selected
   d=$(echo ${!di}) # evaluated

   curl -s -X GET -H "$ct" $url/api/price --data "$d" | "$pp"
   curl -s -X GET -H "$ct" $url/api/eta   --data "$d" | "$pp" 
   curl -s -X GET -H "$ct" $url/api/co    --data "$d" | "$pp" 
 done

 set +x
 docker logs -t $cn

 echo $(date)
 t1=$(date +%s)
 echo "time elapsed `expr $t1 - $t0` sec."
}
