from django.core.management import BaseCommand, call_command


# Не по заданию. Для удобства начального заполнения.
class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Loading fixture information for testing shop...')

        # Альтернативно для гарантии имени можно использовать: shopapp/fixtures/orders-fixture.json
        call_command('loaddata', 'users-fixture.json', 'products-fixture.json', 'orders-fixture.json')

        # У загруженных пользователей нет myauth.Profile. Нужно создать новые.
        call_command('create_profiles')

        print('Loading finished')
