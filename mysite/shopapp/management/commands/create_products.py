from django.core.management import BaseCommand

from shopapp.models import Product


class Command(BaseCommand):
    """
    Creates three test example products
    """

    def handle(self, *args, **options):
        self.stdout.write('Creating products...')

        settings = [
            ('HDD', 5000),
            ('SSD', 7000),
            ('Flash drive', 1000),
        ]

        for element in settings:
            # get_or_create(), чтобы не создавать дубли при повторном вызове.
            # При наличии нескольких Product с одинаковым name возникнет исключение. У name нет ограничений на
            # уникальность. Но такой ситуации не возникнет, так как Product создаются только этой командой.
            # В будущем обработать такую ситуацию можно, например, при помощи Product.objects.filter().first().
            product, created = Product.objects.get_or_create(name=element[0])

            if created:
                product.price=element[1] # Заполнение дополнительных полей
                product.save()

                print('Created:', element[0])

        self.stdout.write(self.style.SUCCESS('Products creation completed'))
