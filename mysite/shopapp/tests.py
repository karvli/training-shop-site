from random import choices
from string import ascii_letters, digits

from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

from shopapp.models import Order, Product
from shopapp.utils import add_two_numbers


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        permission = Permission.objects.get(
            content_type=ContentType.objects.get_for_model(Order), # Отбор по Order именно из shopapp
            codename='view_order',
        )

        # Пользователь со случайными данными при каждом запуске тестов
        user = User.objects.create_user(
            username=''.join(choices(ascii_letters, k=10)),
            password=''.join(choices(ascii_letters, k=10)),
        )
        user.user_permissions.add(permission) # Отдельное сохранение .save() не нужно

        cls.user = user

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)
        self.order = Order.objects.create(
            user=self.user,
            delivery_address=''.join(choices(ascii_letters, k=20)),
            promocode=''.join(choices(digits, k=5)), # Только из цифр, чтобы гарантированно не пересечься с адресом
        )

    def tearDown(self):
        self.order.delete()

    def test_order_details(self):
        response = self.client.get(reverse('shopapp:order_details', kwargs={'pk': self.order.pk}))
        self.assertContains(response, self.order.delivery_address, msg_prefix='Address search')
        self.assertContains(response, self.order.promocode, msg_prefix='Promocode search')
        self.assertEqual(self.order.pk, response.context['object'].pk) # Сравнение с self.order тоже отработало бы


class OrdersExportTestCase(TestCase):
    # При использовании на Windows команды:
    # python .\manage.py dumpdata shopapp.Product > shopapp/fixtures/products-fixture.json
    # при выполнении теста может возникнуть ошибка:
    # UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte
    # Она связана с применения BOM в Windows. Способы исправления:
    # 1. Перед выполнением команды вызвать в терминале команду изменения кодировки:
    # chcp 65001
    # 2. Использовать "--output" вместо ">".
    # python .\manage.py dumpdata shopapp.Product --output shopapp/fixtures/products-fixture.json
    #
    # Другая проблема связана с выгрузкой групп User, которых нет:
    # django.db.utils.IntegrityError: The row in table 'auth_user_groups' with primary key '1' has an invalid foreign key: auth_user_groups.group_id contains a value '1' that does not have a corresponding value in auth_group.id.
    # Через "--exclude" их не отключить. Всё равно выгрузит.
    # python manage.py dumpdata auth.User --exclude auth.group --output shopapp/fixtures/users-fixture.json
    # Обходные решения: удалить лишнее вручную. Или выгрузить целиком все данные авторизации:
    # python manage.py dumpdata auth --output shopapp/fixtures/users-fixture.json
    # Так как в тестовом файле используется три пользователя, выбран первый вариант.
    fixtures = [
        'users-fixture.json',
        'products-fixture.json',
        'orders-fixture.json',
    ]

    @classmethod
    def setUpClass(cls):
        super().setUpClass() # Без этого не загрузятся fixtures

        # Пользователь со случайными данными при каждом запуске тестов
        cls.user = User.objects.create_user(
            username=''.join(choices(ascii_letters, k=10)),
            password=''.join(choices(ascii_letters, k=10)),
            is_staff=True,
        )

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self):
        self.client.force_login(self.user)

    def test_order_export(self):
        response = self.client.get(reverse('shopapp:orders_export'))
        self.assertEqual(response.status_code, 200)
        expected = [
            {
                'id': order.pk,
                'delivery_address': order.delivery_address,
                'promocode': order.promocode,
                'user_id': order.user.pk,
                'produsts': [product.pk for product in order.products.all()]
            }
            for order in Order.objects.select_related('user').prefetch_related('products').all()
        ]

        # Важна сортировка данных
        self.assertEqual(
            response.json()['orders'],
            expected,
        )


# Тестовое из видео курса
class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(2, 3)
        self.assertEqual(result, 5)


class ProductCreateViewTestCase(TestCase):
    def setUp(self) -> None:
        self.product_name = "".join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_create_product(self):
        response = self.client.post(
            reverse('shopapp:product_create'),
            {
                "name": self.product_name,
                "price": '123.45',
                "description": 'A good table',
                "discount": '10',
            }
        )

        # После реализации проверки регистрации тест выдаст ошибку:
        # self.assertRedirects(response, reverse("shopapp:products_list"))
        # self.assertTrue(
        #     Product.objects.filter(name=self.product_name).exists()
        # )
        # Проверка заменена на анализ redirect на страницу LOGIN_URL.
        # Url будет состоять из LOGIN_URL и параметра пути "next" для возврата на предыдущую страницу.
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        # будет выполнено перед всеми тестами в классе
        cls.product = Product.objects.create(name="Best Product")

    @classmethod
    def tearDownClass(cls):
        # будет выполнено после всех тестов в классе
        cls.product.delete()

    # def setUp(self):
    #     # будет выполнено перед каждым тестом
    #     self.product = Product.objects.create(name="Best Product")
    #
    # def tearDown(self):
    #     # будет выполнено после каждого теста
    #     self.product.delete()

    def test_get_product(self):
        response = self.client.get(
            reverse('shopapp:product_details', kwargs={"pk": self.product.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_content(self):
        response = self.client.get(
            reverse('shopapp:product_details', kwargs={"pk": self.product.pk})
        )
        self.assertContains(response, self.product.name)


class ProductsListViewTestVase(TestCase):
    fixtures = [
        'products-fixture.json',
    ]

    def test_products(self):
        response = self.client.get(reverse('shopapp:products_list'))
        self.assertQuerySetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=(p.pk for p in response.context['items']),
            transform=lambda p: p.pk,
        )
        self.assertTemplateUsed(response, 'shopapp/products-list.html')


class OrdersListViewTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username='bob_test', password='qwerty')

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_orders_view(self):
        response = self.client.get(reverse('shopapp:orders_list'))
        self.assertContains(response, 'Orders')

    def test_orders_view_not_authenticated(self):
        self.client.logout()
        response = self.client.get(reverse('shopapp:orders_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class ProductsExportViewTestCase(TestCase):
    fixtures = [
        'products-fixture.json',
    ]

    def test_get_products_view(self):
        response = self.client.get(reverse('shopapp:products-export'))
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by('pk').all()
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived,
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(
            products_data["products"],
            expected_data,
        )