"""
Updates Voters in database based on an input voter file. This function:
 - Adds new voters that don't previously have a voter ID in the database
 - Updates information for existing voters, using the specified fields. If the
   voter is now inactive, unset the foreign key in connected ValidationRecords.

TODO: Add support for voters no longer in voter file, or address changing?
Very rare case for most campaigns, and elections officials seem to set them
to Inactive first.

Usage:
   python update_voters.py <voter_file_path> [--dry_run]
"""
import csv

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


def save_zip(voter, raw_zip):
    voter.res_addr_zip = raw_zip[:5]


# Some fields need additional changes. Values are functions taking Voter and raw
# parameter value.
ADD_CHANGES_FIELDS = {
    'sSitusZip': save_zip,
}


class Command(BaseCommand):
    help = 'Updates Voters based on a new master voter file'

    def add_arguments(self, parser):
        parser.add_argument('voter_file', type=str)
        parser.add_argument("--dry_run", action="store_true",
                            default=False, help="Dry run doesn't change DB.")

    def handle(self, *args, **options):
        # Count voters added or modified, and number of validation records
        # invalidated.
        voters_add = 0
        voters_mod = 0
        vrs_invalidated = 0

        dry_run = options['dry_run']
        try:
            with transaction.atomic():
                with open(options['voter_file'], 'r', encoding='latin1') \
                        as vf_tsv:
                    tsv_reader = csv.DictReader(vf_tsv, delimiter='\t')
                    count = 0
                    for row in tsv_reader:
                        # Create Voter based on row fields
                        voter = Voter()
                        for vf_name, field_name in VOTER_FILE_MAPPING.items():
                            setattr(voter, field_name, row[vf_name])
                        for vf_name, setter in ADD_CHANGES_FIELDS.items():
                            setter(voter, row[vf_name])

                        # Check if voter exists.
                        existing_voter = Voter.objects.filter(
                            voter_id=voter.voter_id)
                        if existing_voter.count() > 0:
                            # Voter already exists in voter file.
                            existing_voter = existing_voter.get()
                            for field_name in VOTER_FILE_MAPPING.values():
                                setattr(existing_voter, field_name,
                                        getattr(voter, field_name))
                            for vf_name, setter in ADD_CHANGES_FIELDS.items():
                                setter(existing_voter, row[vf_name])

                            # Invalidate validation records if voter is inactive
                            if existing_voter.reg_status == \
                                    RegStatus.INACTIVE.value:
                                for vr in existing_voter\
                                        .validationrecord_set.all():
                                    vr.voter = None
                                    vr.save()
                                    vrs_invalidated += 1
                            existing_voter.save()
                            voters_mod += 1
                        else:
                            # New voter
                            voter.save()
                            voters_add += 1

                        count += 1
                        if count % 1000 == 0:
                            self.stdout.write(
                                "\nVoters added: %d.\nVoters modified: %d."
                                "\nValidation records invalidated: %d." %
                                (voters_add, voters_mod, vrs_invalidated))

                self.stdout.write("\n\n\nFinal results:")
                # Do nothing for dry run
                if dry_run:
                    self.stdout.write(
                        "Voters added: %d.\nVoters modified: %d."
                        "\nValidation records invalidated: %d." %
                        (voters_add, voters_mod, vrs_invalidated))
                    raise CommandError("Not saving because this is a dry run")

                self.stdout.write(self.style.WARNING(
                    "Transaction almost successful!"))
                self.stdout.write(self.style.WARNING(
                    "Voters added: %d.\nVoters modified: %d."
                    "\nValidation records invalidated: %d." %
                    (voters_add, voters_mod, vrs_invalidated)))

                confirm = input("\nConfirm whether to update database [y/N]: ")
                if confirm.lower() != "y":
                    raise CommandError("You cancelled the transaction")
            self.stderr.write(self.style.SUCCESS("Transaction successful!"))
        except Exception as e:
            self.stderr.write(self.style.ERROR("Exception: %s" % e))
