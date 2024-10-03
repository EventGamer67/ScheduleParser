from broker import parser_celery_app
from parser import methods
import asyncio


@parser_celery_app.task
def get_latest_zamena_link():
    return methods.get_latest_zamena_link()


@parser_celery_app.task
def get_latest_zamena_link_telegram(chat_id):
    return methods.get_latest_zamena_link_telegram(chat_id)


@parser_celery_app.task
def check_new():
    print("TASK RUN")
    return asyncio.run(methods.check_new())
