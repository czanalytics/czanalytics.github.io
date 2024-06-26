# Dockerfile.bundle for API the bundle routing plans
# Makefile target api_bundle is provided for testing

FROM python:3

# optional
#ADD .key /
#ADD .key_conf /

ARG D=tmp # data dir

ADD ${D}/ODMatrix2021_N2.csv /
ADD ${D}/nuts-names-21.csv /
ADD ${D}/nuts.csv /
ADD ${D}/nuts3.json /
ADD ${D}/nuts_centroid.csv /

# ADD ${D}/<models> /

ADD conf_lite.json /
ADD api_bundle.py /
ADD bundle.py /
ADD lane.py /
ADD net.py /

# routing using picat http://picat-lang.org/download.html
RUN curl -L >picat.tar.gz http://picat-lang.org/download/picat36_linux64.tar.gz \
 && tar -xzvf picat.tar.gz \
 && rm picat.tar.gz

ADD bundle.pi /Picat/
ADD lane.pi /Picat/
ADD pdp.pi /Picat/

RUN pip install flask
RUN pip install flask_restful
RUN pip install flask-expects-json
RUN pip install flask-cors

RUN pip install pandas
RUN pip install numpy
RUN pip install geopy
RUN pip install datetime
RUN pip install geopy

CMD ["python", "./api_bundle.py"]

