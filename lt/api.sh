# api.sh
#
# source api.sh && api > tmp.txt
api() { 
 # test api functionality
 echo "fn:"${FUNCNAME[*]}
 DateTag=$(date)
 echo "   : " $DateTag
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

 hjson="Content-type: application/json"
 
 d1='{"date":"2023-07-01", "from_lat":60.192059, "from_lon":24.945831, "to_lat":60.205490, "to_lon":24.655899}'
 d2='{"date":"2023-07-02", "from_lat":60.192059, "from_lon":24.945831, "to_lat":60.305490, "to_lon":24.755899}'
 d3='{"date":"2023-07-03", "from_lat":60.192059, "from_lon":24.945831, "to_lat":60.405490, "to_lon":24.855899}'
 d4='{"date":"2023-07-04", "from_lat":60.192059, "from_lon":24.945831, "to_lat":60.505490, "to_lon":24.955899}'

 # testing api endpoints

 curl -s "$url"/api        | "$pp" # prettyprinted with silent -s

 curl -s -X GET  -H "$hjson" $url/api/price --data "$d1" | "$pp" # price
 curl -s -X GET  -H "$hjson" $url/api/price --data "$d2" | "$pp"
 curl -s -X GET  -H "$hjson" $url/api/price --data "$d3" | "$pp"
 curl -s -X GET  -H "$hjson" $url/api/price --data "$d4" | "$pp"

 curl -s -X GET  -H "$hjson" $url/api/eta   --data "$d1" | "$pp" # eta
 curl -s -X GET  -H "$hjson" $url/api/eta   --data "$d2" | "$pp"
 curl -s -X GET  -H "$hjson" $url/api/eta   --data "$d3" | "$pp"
 curl -s -X GET  -H "$hjson" $url/api/eta   --data "$d4" | "$pp"
 
 curl -s -X GET  -H "$hjson" $url/api/co    --data "$d1" | "$pp" # co
 curl -s -X GET  -H "$hjson" $url/api/co    --data "$d2" | "$pp"
 curl -s -X GET  -H "$hjson" $url/api/co    --data "$d3" | "$pp"
 curl -s -X GET  -H "$hjson" $url/api/co    --data "$d4" | "$pp"

 set +x
 docker logs -t $conn
 echo $(date)
}

