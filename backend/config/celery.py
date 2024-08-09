from __future__ import absolute_import

import os
from datetime import timedelta

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.config_from_object('config.settings', namespace='CELERY')
app.conf.update(
    worker_concurrency=5,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=50,
    broker_transport_options={
        'max_retries': 3, 'interval_start': 0,
        'interval_step': 0.5, 'interval_max': 2
    },
)

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'task-every-15-sec': {
        'task': 'apps.core.tasks.test_tasks.test_periodic_task',
        'schedule': timedelta(seconds=15),
        'args': ('value1',),
    },
    # 'doctor_score_update_schedule': {
    #     'task': 'app.tasks.doctor_score_update_task',
    #     'schedule': crontab(
    #         minute=f'{settings.TASK_PERIOD_MIN}', hour=f'{settings.TASK_PERIOD_HOUR}'
    #     ),
    #     'options': {'queue': celery_queue},
    # },
    # 'end_of_past_sessions_schedule': {
    #     'task': 'app.tasks.end_of_past_sessions_task',
    #     'schedule': crontab(
    #         minute=f'{settings.TASK_PERIOD_MIN_2}', hour=f'{settings.TASK_PERIOD_HOUR_2}'
    #     ),
    #     'options': {  'queue': celery_queue},
    # },
    # 'define_user_statuses_task_schedule': {
    #     'task': 'app.tasks.define_user_statuses_task',
    #     'schedule': crontab(
    #         minute=f'{settings.TASK_PERIOD_MIN_3}', hour=f'{settings.TASK_PERIOD_HOUR_3}'
    #     ),
    #     'options': {'queue': celery_queue},
    # },
    # 'repeat_purchase_rate_task_schedule': {
    #     'task': 'app.tasks.repeat_purchase_rate_task',
    #     'schedule': crontab(
    #         minute=f'{settings.TASK_PERIOD_MIN_4}', hour=f'{settings.TASK_PERIOD_HOUR_4}'
    #     ),
    #     'options': {'queue': celery_queue},
    # },
    # 'ltv_calculation_task_schedule': {
    #     'task': 'app.tasks.ltv_calculation_task',
    #     'schedule': crontab(
    #         minute=f'{settings.TASK_PERIOD_MIN_5}', hour=f'{settings.TASK_PERIOD_HOUR_5}'
    #     ),
    #     'options': {'queue': celery_queue},
    # },
    # 'cancellation_booking_task_schedule': {
    #     'task': 'app.tasks.cancellation_booking_task',
    #     'schedule': crontab(
    #         minute=f'{settings.TASK_PERIOD_MIN_6}', hour=f'{settings.TASK_PERIOD_HOUR_6}'
    #     ),
    #     'options': {'queue': celery_queue},
    # },
    # 'send_daily_report': {
    #     'task': 'notification.tasks.email_tasks.send_daily_report',
    #     'schedule': crontab(
    #         minute=f'{settings.TASK_PERIOD_MIN_7}', hour=f'{settings.TASK_PERIOD_HOUR_7}'
    #     ),
    #     'options': {'queue': celery_queue},
    # },
    # 'send_lead_report': {
    #     'task': 'notification.tasks.email_tasks.send_lead_report',
    #     'schedule': crontab(
    #         minute=f'{settings.TASK_PERIOD_MIN_8}', hour=f'{settings.TASK_PERIOD_HOUR_8}'
    #     ),
    #     'options': {'queue': celery_queue},
    # },
    # 'send_email_notification_new_message_chat': {
    #     'task': 'notification.tasks.email_tasks.send_email_notification_new_message',
    #     'schedule': crontab(minute='*/5'),
    #     'options': {'queue': celery_queue},
    # },
}
