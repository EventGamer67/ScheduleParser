from celery import Celery
from urllib.request import urlopen
from bs4 import BeautifulSoup
from celery import shared_task

# from broker import parser_celery_app
from src.code.core.schedule_parser import getLastZamenaLink


parser_celery_app = Celery(
    'parser',
    broker='amqp://guest:guest@rabbitmq:5672//',  # Используйте 127.0.0.1 для RabbitMQ
    backend='redis://redis:6379/0'  # Используйте 127.0.0.1 для Redis
)


@parser_celery_app.task
def get_latest_zamena_link():
    try:
        html = urlopen("https://www.uksivt.ru/zameny").read()
        soup: BeautifulSoup = BeautifulSoup(html, 'html.parser')
        link, date = getLastZamenaLink(soup=soup)
        #parser_celery_app.send_task('telegram.send_message_via_bot', args=[chat_id, f"Последняя замена\n{date}\n{link}"])
        return {'date': date, 'link': link}
    except:
        #parser_celery_app.send_task('telegram.send_message_via_bot', args=[-1, "Ошибка"])
        return {'message': 'failed'}


# @parser_celery_app.tasks
# def


print("***")
print(parser_celery_app.tasks.keys())
print("***")