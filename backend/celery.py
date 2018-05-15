"""
Celery setup. Note that we don't store results.
"""

from __future__ import absolute_import

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

from django.conf import settings  # noqa

# Run startup functions before starting Celery.
app = Celery('backend', include=['voter_validation.tasks'])
app.config_from_object(settings)

app.conf.update(
    BROKER_URL=os.environ.get("RABBITMQ_BIGWIG_URL", "amqp://localhost/"),
    BROKER_POOL_LIMIT=1,

    CELERY_RESULT_BACKEND='amqp',
    CELERY_TASK_RESULT_EXPIRES=3600,

    CELERY_ENABLE_UTC=True,
    CELERY_TIMEZONE='America/Los_Angeles',
    CELERY_ACCEPT_CONTENT=['pickle', 'json', 'msgpack', 'yaml'],
)
