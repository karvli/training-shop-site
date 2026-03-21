from django.contrib.auth.models import User
from django.core.management import BaseCommand

from shopapp.models import Order, Product


class Command(BaseCommand):
    """
    Creates three test example orders
    """

    def handle(self, *args, **options):
        self.stdout.write('Creating orders...')

        # Создание заказов до создания пользователей не предполагается.
        # Предполагается наличие в базе обязательного пользователя с именем "admin".
        # Сделано по аналогии с видео курса.
        user = User.objects.get(username='admin')

        # Заказы с уникальными настройками.
        # При наличии нескольких Order с одинаковым настройками возникнет исключение.
        # Но такой ситуации не возникнет, так как Order создаются только этой командой.
        # В будущем обработать такую ситуацию можно, например, при помощи Order.objects.filter().first().
        settings = [
            {
                'promocode': 'SALE',
            },
            {
                'delivery_address': 'Russia, Moscow',
            },
            {
                'promocode': 'WINTER',
                'delivery_address': 'Russia, Siberia',
            },
        ]

        # Всего три продукта. Они также создаются через команду - create_products.
        # Преобразование в list, чтобы не читать повторно при расчёте количества
        products = list(Product.objects.all())

        for index, setting in enumerate(settings):
            order, created = Order.objects.get_or_create(
                user=user,
                **setting
            )

            if created:
                # Сокращение списка продуктов, чтобы заказы немного отличались
                if index == 1 and len(products) > 1:
                    products_chunk = products[1:]
                elif index == 2 and len(products) > 1:
                    products_chunk = products[:-1]
                else:
                    products_chunk = products

                for product in products_chunk:
                    order.products.add(product)

                order.save()

                print('Created order with id', order.pk)

        self.stdout.write(self.style.SUCCESS('Orders creation completed'))