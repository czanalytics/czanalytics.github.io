# api.sh
#
# source api.sh && api > tmp.txt; vim tmp.txt
api() { 
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

 # test_clean  # rm exited containers
 # build new, rm deletes old image

 docker build -t $con . -f Dockerfile."$con"  --force-rm=true 
 
 # -d for detached mode in bg
 docker run -d -p 3333:3333 --name $conn $con
 
 sleep 3

 hjson="Content-type: application/json"
 

 d1='{"id":"00001", "lane":1, "mode":"trailer.o1", "distance":10}'
 d2='{"id":"00002", "lane":2, "mode":"trailer.o4", "distance":100}'
 d3='{"id":"00003", "lane":3, "mode":"trailer.o4", "distance":500}'
 d4='{"id":"00004", "lane":4, "mode":"roro",       "distance":1000}'

 echo "curl>>"

 curl -s -v $url

 curl -s "$url"/api        | "$pp"

 # price
 curl -s -X GET  -H "$hjson" $url/api/price --data "$d1" | "$pp" # prettyprinted with silent -s
 curl -s -X GET  -H "$hjson" $url/api/price --data "$d2" | "$pp"
 curl -s -X GET  -H "$hjson" $url/api/price --data "$d3" | "$pp"
 curl -s -X GET  -H "$hjson" $url/api/price --data "$d4" | "$pp"

 # eta
 curl -s -X GET  -H "$hjson" $url/api/eta   --data "$d1" | "$pp"
 curl -s -X GET  -H "$hjson" $url/api/eta   --data "$d2" | "$pp"
 curl -s -X GET  -H "$hjson" $url/api/eta   --data "$d3" | "$pp"
 curl -s -X GET  -H "$hjson" $url/api/eta   --data "$d4" | "$pp"
 
 # co
 curl -s -X GET  -H "$hjson" $url/api/co    --data "$d1" | "$pp"
 curl -s -X GET  -H "$hjson" $url/api/co    --data "$d2" | "$pp"
 curl -s -X GET  -H "$hjson" $url/api/co    --data "$d3" | "$pp"
 curl -s -X GET  -H "$hjson" $url/api/co    --data "$d4" | "$pp"

 
 echo "<<curl"

 set +x
 docker logs -t $conn
 echo $(date)
}

