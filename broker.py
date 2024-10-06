from celery import Celery
from celery.schedules import crontab

from parser_secrets import BACKEND_URL, BROKER_URL

from src.code.network.supabase_worker import SupaBaseWorker

sup = SupaBaseWorker()

parser_celery_app = Celery(
    "parser",
    broker=BROKER_URL,
    backend=BACKEND_URL,
)
parser_celery_app.conf.broker_connection_retry_on_startup = True
parser_celery_app.autodiscover_tasks(["parser"], force=True)

print("***")
print(parser_celery_app.tasks.keys())
print("***")


parser_celery_app.conf.beat_schedule = {
    "check-new-every-5-minutes": {
        "task": "parser.tasks.check_new",  # Путь к вашей задаче
        "schedule": crontab(
            minute="*/2",
            # hour="6-22"
        ),  # Каждые 5 минут с 6 до 22 часов
        "args": (),  # Аргументы для задачи, если есть
    },
}

parser_celery_app.conf.timezone = "Asia/Yekaterinburg"
