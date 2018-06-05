"""
Updates Voters in database based on an input voter file. This function:
 - Adds new voters that don't previously have a voter ID in the database
 - Updates information for existing voters, using the specified fields. If the
   voter is now inactive, unset the foreign key in connected ValidationRecords.

TODO: Add support for voters no longer in voter file, or address changing?
Very rare case for most campaigns, and elections officials seem to set them
to Inactive first.

Usage:
   python manage.py update_voters <mvf_tsv_url> [--dry_run]

mvf_tsv_url is a URL pointing to where the Master Voter File is stored as a
TSV, e.g. on S3 or Cloudfront.
"""
import codecs
import csv

from contextlib import closing

import requests
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from voter_validation.models import Voter, RegStatus

# Map from voter file field name to the appropriate Voter field in models.py.
VOTER_FILE_MAPPING = {
    'lVoterUniqueID': 'voter_id',
    'szNameFirst': 'first_name',
    'szNameMiddle': 'middle_name',
    'szNameLast': 'last_name',
    'sNameSuffix': 'suffix',

    'szSitusAddress': 'res_addr',
    'szSitusCity': 'res_addr_city',
    'sSitusState': 'res_addr_state',
    'sHouseNum': 'res_addr_house_num',
    'szStreetName': 'res_addr_street_name',
    'sStreetSuffix': 'res_addr_street_suff',
    'sUnitNum': 'res_addr_unit_num',

    'szPhone': 'phone',
    'szEmailAddress': 'email',

    'dtRegDate': 'curr_reg_date',
    'dtOrigRegDate': 'orig_reg_date',
    'sStatusCode': 'reg_status',
    'szStatusReasonDesc': 'reg_status_reason',

    'sGender': 'gender',
    'szPartyName': 'party',
    'szLanguageName': 'language',
}


def transf_zip(raw_zip):
    return raw_zip[:5]


# Some fields need additional changes. Values are functions taking raw parameter
# and transforming it into an acceptable format for the database.
ADD_CHANGES_FIELDS = {
    'sSitusZip': (transf_zip, 'res_addr_zip'),
}


class Command(BaseCommand):
    help = 'Updates Voters based on a new master voter file'

    def __init__(self):
        super(Command, self).__init__()
        # Count voters added or modified, and number of validation records
        # invalidated.
        self.voters_add = 0
        self.voters_unmod = 0  # fields listed at top of file are unmodified
        self.voters_mod = 0
        self.vrs_invalidated = 0

    def add_arguments(self, parser):
        parser.add_argument('mvf_tsv_url', type=str)
        parser.add_argument("--dry_run", action="store_true",
                            default=False, help="Dry run doesn't change DB.")

    def print_counts(self, style=None):
        print_str = "Voters added: %d.\nVoters unmodified: %d." \
                    "\nVoters modified: %d.\nValidation records " \
                    "invalidated: %d.\n\n" %\
                    (self.voters_add, self.voters_unmod, self.voters_mod,
                     self.vrs_invalidated)
        if style:
            print_str = style(print_str)
        self.stdout.write(print_str)

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        url = options['mvf_tsv_url']
        try:
            with transaction.atomic():
                with closing(requests.get(url, stream=True)) as r:
                    tsv_reader = csv.DictReader(
                        codecs.iterdecode(r.iter_lines(), 'latin1'),
                        delimiter='\t')
                    count = 0
                    for row in tsv_reader:
                        # Create Voter based on row fields
                        voter = Voter()
                        for vf_name, field_name in VOTER_FILE_MAPPING.items():
                            setattr(voter, field_name, row[vf_name])
                        for vf_name, (transf, field_name) \
                                in ADD_CHANGES_FIELDS.items():
                            setattr(voter, field_name, transf(row[vf_name]))

                        # Check if voter exists.
                        existing_voter = Voter.objects.filter(
                            voter_id=voter.voter_id)
                        if existing_voter.count() > 0:
                            # Voter already exists in voter file.
                            existing_voter = existing_voter.get()
                            is_modified = False

                            # Check and change modified fields.
                            fields = list(VOTER_FILE_MAPPING.values())
                            fields.extend([f[1] for f in
                                           ADD_CHANGES_FIELDS.values()])
                            for field_name in fields:
                                if getattr(existing_voter, field_name) == \
                                        getattr(voter, field_name):
                                    continue
                                setattr(existing_voter, field_name,
                                        getattr(voter, field_name))
                                is_modified = True

                            # Invalidate validation records if voter is inactive
                            if existing_voter.reg_status == \
                                    RegStatus.INACTIVE.value:
                                for vr in existing_voter\
                                        .validationrecord_set.all():
                                    vr.voter = None
                                    vr.save()
                                    self.vrs_invalidated += 1
                            if is_modified:
                                self.voters_mod += 1
                                existing_voter.save()
                            else:
                                self.voters_unmod += 1
                        else:
                            # New voter
                            voter.save()
                            self.voters_add += 1

                        count += 1
                        if count % 1000 == 0:
                            self.print_counts()

                self.stdout.write("\n\nFinal results:")
                # Do nothing for dry run
                if dry_run:
                    self.print_counts()
                    raise CommandError("Not saving because this is a dry run")

                self.stdout.write(self.style.WARNING(
                    "Transaction almost successful!"))
                self.print_counts(self.style.WARNING)

                confirm = input("\nConfirm whether to update database [y/N]: ")
                if confirm.lower() != "y":
                    raise CommandError("You cancelled the transaction")
            self.stderr.write(self.style.SUCCESS("Transaction successful!"))
        except Exception as e:
            self.stderr.write(self.style.ERROR("Exception: %s" % e))
