# api.sh
#
# source api.sh && api > tmp.txt ; vim tmp.txt
api() { 
 echo "fn:"${FUNCNAME[*]}
 DateTag=$(date)
 echo "   : " $DateTag
 set -x # set echo, set +x unsets

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
 
 d1='{"mode":"truck","distance":1000}'
 d1a='{"cargo_id":"00001", "lane":1, "mode":"trailer.o1", "distance":100}'
 d1b='{"cargo_id":"00002", "lane":1, "mode":"trailer.o4", "distance":1000}'
 d1c='{"cargo_id":"00003", "lane":1, "mode":"trailer.o4", "distance":500}'
 d1d='{"cargo_id":"00003", "lane":2, "mode":"roro",       "distance":500}'

 echo "curl>>"

 curl -s -v $url

 curl -s "$url"/api        | "$pp"
 curl -s "$url"/api/price  | "$pp"
 curl -s "$url"/api/eta    | "$pp"
 curl -s "$url"/api/carbon | "$pp"
 
 # -s for silent
 #curl -s -X GET  -H "$hjson" $url/api/foo --data "$d1" | "$pp"

 # foo
 curl -s -X GET  -H "$hjson" $url/api/foo --data "$d1a" | "$pp" # prettyprinted with silent -s
 curl -s -X GET  -H "$hjson" $url/api/foo --data "$d1b" | "$pp"
 curl -s -X GET  -H "$hjson" $url/api/foo --data "$d1c" | "$pp"
 curl -s -X GET  -H "$hjson" $url/api/foo --data "$d1d" | "$pp"

 # bar
 curl -s -X GET  -H "$hjson" $url/api/bar --data "$d1c" | "$pp"
 curl -s -X GET  -H "$hjson" $url/api/bar --data "$d1d" | "$pp"

 #curl -s -X POST -H "$hjson" $url/api/foo --data "$d1" | "$pp"
 
 echo "<<curl"
 set +x
 docker logs -t $conn
 echo $(date)
}

