# api.sh for testing API service

#tst() {
# da="23-08-01" 
# laam=52.36760; 
# dtemp='{"da":"%s", "lat1":%s}\n' # careful
# d=$(printf  "$dtemp" $da" "$laam")
#
# echo $d
#}

# Browsing https://api-translate.systran.net gives
# {"error":{"statusCode":400,"message":"No key / credentials provided","info":{"authorizationUrl":"https://translate.systran.net/oidc"}}}


api_local() { 
 echo "test api functionality"
 echo "fn:"${FUNCNAME[*]}
 echo $(date)
 t0=$(date +%s)
 set -x # shell echo, set +x unsets
 
 ci="lang"     # image
 cn="$ci"_api  # container

 key="Api-Key: "`cat .key`
 ip="0.0.0.0"; p="8888"; url="http://$ip:$p"
 
 ct="Content-type: application/json"
 pp="json_pp" # prettyprinter

 docker stop $cn # clean
 docker rm   $cn
 docker rmi  $ci

 docker build -t $ci . -f Dockerfile.api --force-rm=true 
 docker run -d -p $p:$p --name $cn $ci  # -d for detached mode in bg
 sleep 3

 curl -H "$key" -s "$url"     | "$pp" # request pp with silent -s
 curl -H "$key" -s "$url"/api | "$pp" 
 
 d='{"text":Hej", "language":"fi"}'

 #d='{"input":"Hello Linda, How are you?", "target":"it"}'
 #curl -H "$key" $url/api/translate --data "$d" | "$pp" 

 curl -X GET -H "$ct" -H "$key" "$url"/api/translate --data "$d" | "$pp"
 
 set +x
 docker logs -t $cn

 echo $(date)
 t1=$(date +%s)
 echo "time elapsed `expr $t1 - $t0` sec."
}


api_tr() { 
 echo "test mt api"
 echo "fn:"${FUNCNAME[*]}
 echo $(date)
 t0=$(date +%s)
 set -x 
 
 #ia=1; ib=8
 #cn="$ci"_api  # container
 # ip="0.0.0.0"; p="3333"; url="http://$ip:$p"
 # Authorization: Key YOUR_API_KEY

 url="https://api-translate.systran.net"
 
 #key="Api-Key: "`cat .key`
 key="Authorization: Key "`cat .key`
 #echo $key
 
 ct="Content-type: application/json"
 
 d='{"input":"Hello Linda, How are you?", "target":"it"}'

 pp="json_pp" # prettyprinter

 curl -X GET -H "$ct" -H "$key" "$url"/api/ --data "$d" | "$pp"

 #POST /translation/text/translate

 #curl -H "$key" -s "$url"     | "$pp"
 #curl -H "$key" -s "$url"/api | "$pp" 
 #curl -s -X GET -H "$ct" -H "$key" $url/api/route --data "$d" | "$pp"

 set +x
 echo $(date)
 t1=$(date +%s)
 echo "time elapsed `expr $t1 - $t0` sec."
}

