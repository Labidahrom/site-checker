from __future__ import absolute_import
import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_checker.settings')

app = Celery('site_checker')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
