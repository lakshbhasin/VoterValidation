from datetime import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from backend.settings import SERVER_TIME_ZONE
from voter_validation.common import ChoiceEnum


class RegStatus(ChoiceEnum):
    """
    One-letter abbreviation to mark a voter's current registration status.
    We only count active voters for validation purposes.
    """
    ACTIVE = 'A'
    INACTIVE = 'I'
    CANCELLED = 'C'
    LOCAL_PENDING = 'P'
    NONE = ''


class Voter(models.Model):
    """
    Represents a registered voter. Most of these fields are varchar for
    convenience and easy interoperability with different voter file formats
    (see common.py).
    """
    # Use county's voter ID as unique ID for consistency. Note: this may make it
    # difficult to run this website for multiple counties if IDs overlap.
    voter_id = models.CharField(max_length=60, default='', primary_key=True)

    # Name-related parameters
    first_name = models.CharField(max_length=32, default='')
    middle_name = models.CharField(max_length=32, default='', blank=True)
    last_name = models.CharField(max_length=32, default='')
    suffix = models.CharField(max_length=32, default='', blank=True)

    # Combination of above name parameters. Created on save.
    full_name = models.CharField(max_length=128, default='', blank=True,
                                 db_index=True)

    # Residential address components. ZIP is shortened from ZIP+4 for simplicity
    # Full address and ZIP are indexed.
    res_addr = models.CharField(max_length=70, default='', db_index=True)
    res_addr_zip = models.CharField(max_length=5, default='', db_index=True)
    res_addr_city = models.CharField(max_length=30, default='')
    res_addr_state = models.CharField(max_length=2, default='')
    res_addr_house_num = models.CharField(max_length=10, default='', blank=True)
    res_addr_street_name = models.CharField(
        max_length=35, default='', blank=True)
    res_addr_street_suff = models.CharField(
        max_length=10, default='', blank=True)
    res_addr_unit_num = models.CharField(
        max_length=8, default='', blank=True)

    # Voter contact information (not shown in UI)
    phone = models.CharField(max_length=14, default='', blank=True)
    email = models.CharField(max_length=100, default='', blank=True)

    # Registration characteristics and status. Dates usually MM/DD/YYYY.
    curr_reg_date = models.CharField(max_length=10, default='', blank=True)
    orig_reg_date = models.CharField(max_length=10, default='', blank=True)
    reg_status = models.CharField(
        max_length=1, choices=RegStatus.choices(), db_index=True,
        default=str(RegStatus.NONE.value))
    reg_status_reason = models.CharField(max_length=50, default='', blank=True)

    # Other voter characteristics
    gender = models.CharField(max_length=1, default='', blank=True)
    party = models.CharField(max_length=50, default='', blank=True)
    language = models.CharField(max_length=16, default='', blank=True)

    def __str__(self):
        return "%s (%s)" % (self.full_name, self.res_addr)

    def save(self, *args, **kwargs):
        """
        Updates the full_name, then saves.
        """
        names = [self.first_name, self.middle_name, self.last_name, self.suffix]
        self.full_name = ' '.join(filter(lambda s: s != '', names))
        super(Voter, self).save(*args, **kwargs)


class Campaign(models.Model):
    """
    Represents an ongoing campaign that is doing voter validation. Note that
    these have an autoincrementing primary key (pk) field that is implicit in
    Django.
    """
    name = models.CharField(max_length=60, default='')
    validation_goal = models.IntegerField(default=1000)

    def __str__(self):
        return self.name

    def validation_count(self):
        """
        Count the number of ValidationRecords for this campaign that are for
        non-null Voters (i.e. still valid) with ACTIVE registration status.
        """
        return self.validationrecord_set.filter(
            voter__reg_status=RegStatus.ACTIVE.value,
            voter__isnull=False)\
            .count()


class UserProfile(models.Model):
    """
    Model for a User profile, which adds extra information to the base Django
    User class.

    Users here represent data entry staff or volunteers, and are associated
    with campaigns.
    """
    user = models.OneToOneField(User, primary_key=True, verbose_name="User")
    campaigns = models.ManyToManyField(Campaign)

    def __str__(self):
        return "%s (Campaigns: %s)" % \
               (self.user.username,
                ', '.join(str(c) for c in self.campaigns.all()))

    def in_campaign(self, campaign_id):
        campaign_id = int(campaign_id)
        for campaign in self.campaigns.all():
            if campaign.pk == campaign_id:
                return True
        return False


class ValidationRecord(models.Model):
    """
    Marks a validated Voter for a given Campaign. Note that (campaign_id,
    voter_id) must be unique since we can't validate a Voter twice.

    Some voter fields are denormalized as backup in case a Voter is
    accidentally wiped by a voter file update.
    """
    # Who validated this Voter, and date of last update for record
    validator = models.ForeignKey(UserProfile, null=True,
                                  on_delete=models.SET_NULL)
    last_updated = models.DateTimeField(default=timezone.now, blank=True,
                                        db_index=True)

    # Campaign this Voter was validated for, and PK (for uniqueness constraint)
    campaign = models.ForeignKey(Campaign, null=True, on_delete=models.SET_NULL,
                                 db_index=True)
    campaign_pk = models.IntegerField(blank=True)

    # Voter information, including denormalized fields for backup.
    voter = models.ForeignKey(Voter, null=True, on_delete=models.SET_NULL)
    voter_full_name = models.CharField(max_length=100, default='', blank=True)
    voter_res_address = models.CharField(max_length=70, default='', blank=True)
    voter_uid = models.CharField(max_length=60, default='', blank=True)

    class Meta:
        unique_together = (("campaign_pk", "voter_uid"),)

    def save(self, *args, **kwargs):
        """
        Updates the last_updated field, voter name/address (if set), then saves.
        """
        self.last_updated = datetime.now(SERVER_TIME_ZONE)
        if self.campaign is not None:
            self.campaign_pk = self.campaign.pk
        if self.voter is not None:
            # Denormalized fields for backup.
            self.voter_full_name = self.voter.full_name
            self.voter_res_address = self.voter.res_addr
            self.voter_uid = self.voter.voter_id
        super(ValidationRecord, self).save(*args, **kwargs)

    def __str__(self):
        return "%s validated %s for %s" % \
               (self.validator.user.username, self.voter.full_name,
                self.campaign.name)
