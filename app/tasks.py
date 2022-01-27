import os
import time
from celery import Celery
from celery.schedules import crontab
from datetime import datetime

from .dash.biz_insights import data_parsing
from .dash.biz_insights import getThreads


CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379'),
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379')

PSQL_HOST = os.environ.get('PSQL_HOST', '127.0.0.1')


celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)


@celery.task(name='tasks.add')
def add(x: int, y: int) -> int:
    time.sleep(5)
    return x + y

@celery.task(name='tasks.check')
def check():
 print("I am checking your stuff")

@celery.task(name='tasks.regenGraphData')
def regenGraphData():
    # updates formatting data pickle 
    data_parsing.updateAllTickerData()

@celery.task(name='tasks.getNewChanData')
def getNewChanData():
    # If db is being called through a ssh tunnel port (locally) don't run
    if PSQL_HOST != "127.0.0.1":
        getThreads.LoopPages()

 

celery.conf.beat_schedule = {
    # "run-me-every-ten-seconds": {
    #     "task": "tasks.check",
    #     "schedule": 10.0
    # },
    "scrap-recent-chan-data": {
        "task": "tasks.getNewChanData",
        'schedule': crontab(minute=(datetime.now().minute + 1) % 10)
    },
    "regenGraph": {
        "task": "tasks.regenGraphData",
        'schedule': crontab(minute=(datetime.now().minute + 2) % 180), #Runs hourly starting 2 minutes from app start https://stackoverflow.com/questions/31764528/running-celery-task-when-celery-beat-starts
    }
}
