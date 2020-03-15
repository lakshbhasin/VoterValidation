from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from voter_validation.models import UserProfile


class Command(BaseCommand):
    help = 'Creates a UserProfile for a User already created by createsuperuser.'

    def add_arguments(self, parser):
        parser.add_argument('user', nargs='+', type=str)

    def handle(self, *args, **options):
        for username in options['user']:
            try:
                admin = User.objects.filter(username=username).get()
                user_profile = UserProfile(user=admin)
            except Exception as e:
                raise CommandError('User "%s" does not exist: %s' % username, e)

            user_profile.save()
            self.stdout.write(self.style.SUCCESS(
                    'Successfully created user "%s"' % username))
