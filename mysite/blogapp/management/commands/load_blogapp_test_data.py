from django.core.management import BaseCommand, call_command


# Не по заданию. Для удобства начального заполнения.
class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Loading fixture information for testing blog...')

        # Альтернативно для гарантии имени можно использовать: blogapp/fixtures/blogapp-test-data-fixture.json
        call_command('loaddata', 'blogapp-test-data-fixture.json')

        print('Loading finished')
