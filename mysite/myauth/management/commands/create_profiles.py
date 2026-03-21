from django.contrib.auth.models import User
from django.core.management import BaseCommand

from myauth.models import Profile


# Сделано не по заданию. Для начального заполнения профилей.
class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Creating user profiles...')

        # select_related не нужен, так как profile не используется
        users = User.objects.filter(profile__isnull=True)

        new_profiles = [Profile(user=user) for user in users]
        Profile.objects.bulk_create(new_profiles)

        print('Cerated user profiles:', len(new_profiles))
