# Dockerfile api testing
# Usage: docker build .
# https://www.docker.com/blog/containerizing-test-tooling-creating-your-dockerfile-and-makefile/ 
# https://docs.docker.com/engine/reference/commandline/build/

FROM python:3

WORKDIR /lt

COPY ./.key ./.key
COPY ./.key_conf ./.key_conf

COPY ./tmp/ODMatrix2021_N2.csv ./tmp/ODMatrix2021_N2.csv
COPY ./tmp/nuts-names-21.csv ./tmp/nuts-names-21.csv
COPY ./tmp/nuts.csv ./tmp/nuts.csv
COPY ./tmp/nuts3.json ./tmp/nuts.csv
COPY ./tmp/nuts_centroid.csv ./tmp/nuts_centroid.csv

COPY ./Makefile ./Makefile

COPY ./conf_lite.json ./conf_lite.json

COPY ./api.py ./api.py
COPY ./lane.py ./lane.py
COPY ./net.py ./net.py

RUN apt update && apt install -y make

RUN pip install flask
RUN pip install flask_restful
RUN pip install flask-expects-json
RUN pip install flask-cors

RUN pip install pandas
RUN pip install numpy
RUN pip install geopy
RUN pip install datetime
RUN pip install geopy

RUN make api-img
