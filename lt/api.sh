# api.sh
#
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
 d1='{"date":"2023-07-01", "from_lat":60.192059, "from_lon":24.945831, "to_lat":60.205490, "to_lon":24.655899}'
 d2='{"date":"2023-07-02", "from_lat":60.192059, "from_lon":24.945831, "to_lat":60.305490, "to_lon":24.755899}'
 d3='{"date":"2023-07-03", "from_lat":60.192059, "from_lon":24.945831, "to_lat":60.405490, "to_lon":24.855899}'
 d4='{"date":"2023-07-04", "from_lat":60.192059, "from_lon":24.945831, "to_lat":60.505490, "to_lon":24.955899}'
 
 docker stop $cn #  clean
 docker rm   $cn
 docker rmi  $ci

 docker build -t $ci . -f Dockerfile."$ci" --force-rm=true 
 
 docker run -d -p $p:$p --name $cn $ci  # -d for detached mode in bg
 
 sleep 3

 curl -s "$url"/api | "$pp" # request pp with silent -s

 for i in {1..4}
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

