import datetime
from csv import DictReader
from io import TextIOWrapper
from itertools import product

from django.contrib import admin
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls import path

from .common import save_csv_products
from .models import Product, Order, ProductImage
from .admin_mixins import ExportAsCSVMixin
from .forms import CSVImportForm


@admin.action(description='Archive products')
def mark_archived(model: admin.ModelAdmin, request: HttpRequest, query_set: QuerySet[Product]):
    query_set.update(archived=True)


# В задании требовалась только архивация. Но логично предусмотреть и обратную операцию.
@admin.action(description='Unarchive products')
def mark_unarchived(model: admin.ModelAdmin, request: HttpRequest, query_set: QuerySet[Product]):
    query_set.update(archived=False)


class OrderInline(admin.StackedInline):
    # PyCharm не отобразил "orders" в подсказке ввода.
    model = Product.orders.through
    # Можно и так (см. ниже). Это одна и та же модель таблицы.
    # Но рекомендуется для наглядности брать из таблицы, из которой выполняется отбор (см. выше).
    # model = Order.products.through


# Не из задания
class ProductInline(admin.StackedInline):
    model = ProductImage


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin, ExportAsCSVMixin):
    change_list_template = "shopapp/products_changelist.html"
    actions = [
        mark_archived,
        mark_unarchived,
        "export_as_csv",
    ]
    inlines = [
        OrderInline,
        ProductInline,
    ]
    list_display = 'pk', 'name', 'price', 'discount', 'description_short', 'created_at', 'archived'
    list_display_links = 'pk', 'name' # Для удобства. В задании не требовалось.
    ordering = 'name', '-created_at' # Для удобства. В задании не требовалось.
    search_fields = 'name', 'description', 'price', 'discount'
    fieldsets = [
        (None, {
            'fields': ['name', 'description'],
        }),
        ('Price info', {
            'fields': ['price', 'discount'],
            'classes': ['wide'], # 'wide' - широкий отступ между заголовком и полем. В задании не требовалось.
        }),

        # Не из задания
        ("Images", {
            "fields": ("preview",),
        }),

        ('Extra options', {
            'fields': ['archived'],
            'classes': ['collapse'],
            "description": "Extra options. Field 'archived' is for soft delete.",
        }),
    ]

    # Для удобства. В задании не требовалось.
    # Длинные строки сокращаются, чтобы не занимать лишнее место.
    def description_short(self, obj: Product):
        text = obj.description
        return f"{text[:47]}..." if len(text) > 50 else text

    def get_queryset(self, request):
        # Связанные данные получаются для одного продукта.
        # Поэтому ".prefetch_related('orders')" просто "хорошая практика".
        return Product.objects.prefetch_related('orders')

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == "GET":
            form = CSVImportForm()
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context)
        form = CSVImportForm(request.POST, request.FILES)
        if not form.is_valid():
            context = {
                "form": form,
            }
            return render(request, "admin/csv_form.html", context, status=400)

        save_csv_products(
            file=form.files["csv_file"].file,
            encoding=request.encoding,
        )
        self.message_user(request, "Data from CSV was imported")
        return redirect("..")

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                "import-products-csv/",
                self.import_csv,
                name="import_products_csv",
            ),
        ]
        return new_urls + urls


# Альтернативный вариант регистрации. Без декоратора.
# admin.site.register(Product, ProductAdmin)


class ProductInline(admin.TabularInline):
# Альтернативное отображение:
# class ProductInline(admin.StackedInline):
    model = Order.products.through


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [
        ProductInline,
    ]
    list_display = 'pk', 'created_at', 'user_verbose', 'promocode', 'delivery_address'
    list_display_links = 'pk', 'created_at' # Для удобства. В задании не требовалось.
    ordering = 'created_at', 'pk'  # Для удобства. В задании не требовалось.
    search_fields = 'promocode', 'delivery_address'
    change_list_template = 'shopapp/orders_changelist.html'

    def get_queryset(self, request):
        # Оптимизация получения связанных данных
        return Order.objects.select_related('user').prefetch_related('products')

    def user_verbose(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username

    def import_csv(self, request: HttpRequest) -> HttpResponse:
        if request.method == 'GET':
            form = CSVImportForm()
            context = {
                'form': form,
            }
            return render(request, 'admin/csv_form.html', context)

        form = CSVImportForm(request.POST, request.FILES)

        if not form.is_valid():
            context = {
                'form': form,
            }

            # Данные введены неверно, поэтому ошибка 400 "Bad Request" ("Неправильный запрос")
            return render(request, 'admin/csv_form.html', context, status=400)

        csv_file = TextIOWrapper(
            form.files['csv_file'].file,
            encoding=request.encoding,
        )

        reader = DictReader(csv_file)

        # Пример загружаемого файла в корне проекта: "additional_resources/import_orders_example.csv".
        # Имена полей файла совпадают с именами полей модели.
        # Для упрощения обработки вероятность ошибок поиска НЕ учитывается.
        # Запись без .bulk_create(), так как для заполнения списка products нужны id Order.
        # Можно выполнить оптимизацию запроса User и Product. Пройти reader, сохранить его строки в list, id User и
        # Product в отдельные set, выполнить два запроса, использовать результаты при повторном прохождении строк list.
        for row in reader:
            user = User.objects.get(pk=row['user'])
            product_ids = row['products'].split(',')

            order_data = row.copy()
            order_data.pop('products') # Их надо грузить отдельно. Иначе возникнет ошибка.
            order_data['user'] = user

            # При создании подменяется часть ключей
            order = Order(**order_data)
            order.save() # Чтобы создать id Order, необходимый ниже для настройки поля products

            # Метод "set" позволяет установить сразу несколько Product по их id.
            # Предварительное преобразование str в int не требуется.
            order.products.set(product_ids)

        self.message_user(request, 'Imported data from CSV')

        # Так как эта страница на один уровень ниже списка заказов, можно просто "подняться на один уровень вверх"
        return redirect('..')


    def get_urls(self):
        urls = super().get_urls()
        new_urls = [
            path(
                'import_orders_csv',
                self.import_csv,
                name='import_orders_csv',
            )
        ]

        # "new_urls" обязательно вначале, чтобы их не перекрыли правила из "urls"
        return new_urls + urls
