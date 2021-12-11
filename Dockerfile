FROM tiangolo/uwsgi-nginx-flask:python3.8

ENV CELERY_BROKER_URL redis://redis:6379/0
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true

WORKDIR /app

RUN apt-get update \
    && apt-get install -y ca-certificates

COPY ./requirements.txt /requirements.txt
RUN pip install -U setuptools pip
RUN pip --trusted-host=pypi.python.org --trusted-host=pypi.org --trusted-host=files.pythonhosted.org install -r /requirements.txt

COPY ./ /app
WORKDIR /app