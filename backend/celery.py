"""
Celery setup. Note that we don't store results.
"""

from __future__ import absolute_import

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

from django.conf import settings  # noqa

# Configure celery tasks.
app = Celery('backend', include=['voter_validation.tasks'])
app.config_from_object(settings)

app.conf.update(
    BROKER_URL=os.environ["REDIS_URL"],
    BROKER_POOL_LIMIT=1,

    CELERY_RESULT_BACKEND=os.environ["REDIS_URL"],
    CELERY_TASK_RESULT_EXPIRES=3600,

    CELERY_ENABLE_UTC=True,
    CELERY_TIMEZONE='America/Los_Angeles',
    # Use JSON to serialize task arguments to avoid issues with pickle
    CELERY_ACCEPT_CONTENT=['json'],
    CELERY_TASK_SERIALIZER='json',
)
