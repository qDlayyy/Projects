import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'store.settings')
app = Celery('store')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


app.conf.beat_schedule = {
    'send_every_week_email':{
        'task': 'api.tasks.send_weekly_email',
        'schedule': crontab(day_of_week='tue', hour=8, minute=30)
    }
}