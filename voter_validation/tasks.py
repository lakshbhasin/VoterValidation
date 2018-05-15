"""
Asynchronous and periodic tasks run by Celery, on one worker node. Note that
this uses RabbitMQ, not redis, so the results are not stored anywhere. The
tasks in this module are just supposed to run, and not return results.

Both asynchronous and periodic tasks run on the same Celery worker node. To
run celery, run the following command:

    celery -A call_tracker worker -B -l info -c 4

Where -c represents the concurrency, and -B makes sure we use the celery beat
service (for periodic jobs).
"""
from __future__ import absolute_import  # So we use the right celery

import logging

from celery import shared_task

from voter_validation.models import ValidationRecord

logger = logging.getLogger(__name__)


@shared_task
def validate_voter(voter, campaign, val, validator):
    """
    Validates the given voter for the specified campaign.
    :param voter: Voter
    :param campaign: Campaign for which voter is validated
    :param val: boolean value indicating whether to validate (True) or
    invalidate (False).
    :param validator: UserProfile that validated this campaign.
    :return saved ValidationRecord, or None in the case of invalidation
    """
    # Check if validation record already exists.
    prev_vr = ValidationRecord.objects.filter(voter=voter, campaign=campaign)
    if prev_vr.count() != 0:
        vr = prev_vr.get()
        if val:
            # Already validated, so this is a no-op
            return vr
        else:
            # Remove ValidationRecord entirely
            vr.delete()
            return None
    else:
        if val:
            vr = ValidationRecord(voter=voter, campaign=campaign,
                                  validator=validator)
            vr.save()
            return vr
        else:
            # No-op since there is no existing ValidationRecord
            return None
