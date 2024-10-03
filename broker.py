from celery import Celery
from celery.schedules import crontab

from parser_secrets import BACKEND_URL, BROKER_URL

# from parser.tasks import check_new
from src.code.network.supabase_worker import SupaBaseWorker

sup = SupaBaseWorker()

parser_celery_app = Celery(
    "parser",
    broker=BROKER_URL,
    backend=BACKEND_URL,
)

parser_celery_app.autodiscover_tasks(["parser"], force=True)

print("***")
print(parser_celery_app.tasks.keys())
print("***")


parser_celery_app.conf.beat_schedule = {
    "add-every-30-seconds": {
        "task": "parser.tasks.check_new",
        "schedule": 30.0,
        "args": (),
    },
}
parser_celery_app.conf.timezone = "Asia/Yekaterinburg"
