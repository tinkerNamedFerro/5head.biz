FROM tiangolo/uwsgi-nginx-flask:python3.8
WORKDIR /app

RUN apt-get update \
    && apt-get install -y ca-certificates


COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

COPY ./ /app
WORKDIR /app
