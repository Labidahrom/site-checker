import os
from celery import Celery
import logging
from celery.signals import after_setup_logger, after_setup_task_logger

LOG_FORMAT = '[%(levelname)s/%(processName)s] %(message)s'
LOG_LEVEL = logging.INFO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'site_checker.settings')

app = Celery('site_checker')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

def setup_logging(logfile="celery.log"):
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

    file_handler = logging.FileHandler(logfile)
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S'))
    file_handler.setLevel(LOG_LEVEL)
    root_logger.addHandler(file_handler)


@after_setup_logger.connect
def after_setup_celery_logger(logger, **kwargs):
    setup_logging()


@after_setup_task_logger.connect
def after_setup_celery_task_logger(logger, **kwargs):
    setup_logging()

