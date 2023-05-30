FROM python:3.10.8
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD python memcached2Influx.py -s vldantemon003.lnf.infn.it -po 8086 -k DAFNESTATELAB_JDAT -r 10
