from broker import parser_celery_app
from parser import methods
import asyncio
import functools


def sync(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(f(*args, **kwargs))

    return wrapper


@parser_celery_app.task
def get_latest_zamena_link():
    return methods.get_latest_zamena_link()


@parser_celery_app.task
@sync
async def get_latest_zamena_link_telegram(chat_id):
    return await methods.get_latest_zamena_link_telegram(chat_id)


@parser_celery_app.task
def check_new():
    return asyncio.run(methods.check_new())
