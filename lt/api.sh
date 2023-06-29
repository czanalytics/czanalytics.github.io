# api.sh
#
# source api.sh && api > tmp.txt
api() { 
 # test api functionality
 echo "fn:"${FUNCNAME[*]}
 echo $(date)
 start_time=$(date +%s)
 set -x # shell echo, set +x unsets

 con="api"
 conn="$con"_con
 url="http://0.0.0.0:3333"
 pp="json_pp" # prettyprinting

 docker stop $conn #  cleaning
 docker rm $conn
 docker rmi $con

 docker build -t $con . -f Dockerfile."$con"  --force-rm=true 
 
 docker run -d -p 3333:3333 --name $conn $con  # -d for detached mode in bg
 
 sleep 3
 
 # tests
 d1='{"date":"2023-07-01", "from_lat":60.192059, "from_lon":24.945831, "to_lat":60.205490, "to_lon":24.655899}'
 d2='{"date":"2023-07-02", "from_lat":60.192059, "from_lon":24.945831, "to_lat":60.305490, "to_lon":24.755899}'
 d3='{"date":"2023-07-03", "from_lat":60.192059, "from_lon":24.945831, "to_lat":60.405490, "to_lon":24.855899}'
 d4='{"date":"2023-07-04", "from_lat":60.192059, "from_lon":24.945831, "to_lat":60.505490, "to_lon":24.955899}'
 
 cnt="Content-type: application/json"

 curl -s "$url"/api        | "$pp" # request prettyprinted with silent -s

 for i in {1..4}
 do
   di="d$i"         # select the test
   d=$(echo ${!di}) # evaluate

   curl -s -X GET  -H "$cnt" $url/api/price --data "$d" | "$pp"
   curl -s -X GET  -H "$cnt" $url/api/eta   --data "$d" | "$pp" 
   curl -s -X GET  -H "$cnt" $url/api/co    --data "$d" | "$pp" 
 done

 set +x
 docker logs -t $conn
 echo $(date)
 
 end_time=$(date +%s)
 echo "time elapsed `expr $end_time - $start_time` sec."
}

