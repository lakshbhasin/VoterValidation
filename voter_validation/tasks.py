"""
Asynchronous and periodic tasks run by Celery on one worker node. Note that
this uses redis. The tasks in this module are just supposed to run and interact
with the database, and not return results.

To run celery, see the command in the Procfile.
"""
from __future__ import absolute_import  # So we use the right celery

import logging

from celery import shared_task

from voter_validation.models import ValidationRecord, Voter, Campaign, \
    UserProfile

logger = logging.getLogger(__name__)


@shared_task
def validate_voter(voter_id, campaign_id, val, validator_username):
    """
    Validates the given voter for the specified campaign.
    :param voter_id: Voter ID
    :param campaign_id: Campaign ID for which voter is being validated
    :param val: boolean value indicating whether to validate (True) or
    invalidate (False).
    :param validator_username: username of User that validated this campaign.
    :return saved ValidationRecord, or None in the case of invalidation
    """
    # Look up objects based on given IDs.
    voter = Voter.objects.get(voter_id=voter_id)
    campaign = Campaign.objects.get(pk=campaign_id)
    validator = UserProfile.objects.get(user__username=validator_username)

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
            vr = ValidationRecord(voter=voter,
                                  campaign=campaign,
                                  validator=validator)
            vr.save()
            return vr
        else:
            # No-op since there is no existing ValidationRecord
            return None
