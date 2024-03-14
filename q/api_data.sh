# get resource files

dir='https://raw.githubusercontent.com/czanalytics/multimodal-shipping/main/dat/'

f1='ODMatrix2021_N2.csv'
f2='nuts-names-21.csv'
f3='nuts.csv'
f4='nuts3.json'

rm tmp/*.json tmp/*.csv # clean

wget -P ./tmp $dir$f1
wget -P ./tmp $dir$f2
wget -P ./tmp $dir$f3
wget -P ./tmp $dir$f4
