import logging
from csv import DictWriter

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group, User
from django.contrib.syndication.views import Feed
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .common import save_csv_products
from .forms import ProductForm
from .models import Product, Order, ProductImage
from .serializers import ProductSerializer, OrderSerializer

log = logging.getLogger(__name__) # Не из задания

@cache_page(60 * 2, key_prefix="shop-index-key-prefix") # Не по заданию
def shop_index(request: HttpRequest) -> HttpResponse:
    context = {
        # Демонстрация перехода по прямым ссылкам.
        'pages': [
            {
                'url': 'products/', # Альтернатива: './products/'
                'title': 'Список товаров (продуктов)',
            },
            {
                'url': 'products/export/',
                'title': 'Экспорт товаров (продуктов) в JSON',
            },
            {
                'url': 'products/latest/feed/',
                'title': 'RSS-лента последних товаров (продуктов)',
            },
            {
                'url': 'orders/',
                'title': 'Список заказов',
            },
            {
                'url': 'orders/export/',
                'title': 'Экспорт заказов в JSON',
            },
            {
                'url': 'groups/',
                'title': 'Группы пользователей',
            },
            {
                'url': 'api/',
                'title': 'Документация API (Django)',
            },
        ],

        # Не из задания. "Заглушка" вместо реализации отдельной "главной страницы".
        # Демонстрация перехода по именам ссылок. Более предпочтительный вариант.
        'other_pages': [
            {
                'url': 'admin:index',
                'title': 'Административная панель Django',
            },{
                'url': 'myauth:about-me',
                'title': 'Информация о текущем пользователе',
            },
            {
                'url': 'myauth:register',
                'title': 'Регистрация нового пользователя',
            },
            {
                'url': 'myauth:user_list',
                'title': 'Список пользователей с возможностью перехода к заказам пользователя (обратно в ShopApp)',
            },
            {
                'url': 'blogapp:articles',
                'title': 'Список статей блога',
            },
            {
                'url': 'blogapp:articles-feed',
                'title': 'RSS-лента последних статей блога',
            },
            {
                'url': 'swagger',  # Имена для переадресации. Имеет зависимость от приложений.
                'title': 'Swagger API - общая документация, включающая тестовые API',
            },
            {
                'url': 'django.contrib.sitemaps.views.sitemap',
                'title': 'Карта сайта, содержащая ShopApp и BlogApp',
            },
        ],

        # Не из задания. "Заглушка" вместо реализации отдельной "главной страницы".
        'test_pages': [
            {
                'url': 'requestdataapp:file-upload',
                'title': 'Загрузка файла в каталог "uploaded_files", расположенный в корне проекта',
            },
            {
                'url': 'myauth:cookie-get',
                'title': 'Получение cookie',
            },
            {
                'url': 'myauth:cookie-set',
                'title': 'Установка cookie',
            },
            {
                'url': 'myauth:session-get',
                'title': 'Получение сессии',
            },
            {
                'url': 'myauth:session-set',
                'title': 'Установка сессии',
            },
            {
                'url': 'myauth:foo-bar',
                'title': 'Страница, используемая для демонстрации тестов приложения MyAuth',
            },
        ]
    }

    # Не из задания. Для проверки логирования.
    # Строка и параметр передаются отдельно, чтобы в случае, если сообщение не нужно, не выполнялось склеивание строки.
    log.debug('Shop index pages: %s', context['pages'])
    log.info('Rendering shop index')

    return render(request, 'shopapp/shop-index.html', context=context)


class GroupsListView(ListView):
    template_name = 'shopapp/groups-list.html'
    queryset = Group.objects.prefetch_related('permissions') # Запрос с получением связанных данных
    context_object_name = 'groups' # Переопределение имени списка групп. По умолчанию - "objects".


class ProductListView(ListView):
    template_name = 'shopapp/products-list.html'
    queryset = Product.objects.filter(archived=False) # В списке отображаются только неархивированные
    context_object_name = 'items' # Переопределение имени списка Product. По умолчанию - "objects".


class ProductDetailsView(DetailView):
    template_name = 'shopapp/products-details.html'
    context_object_name = 'product'
    queryset = Product.objects.prefetch_related("images") # images не из задания


class ProductCreateView(PermissionRequiredMixin, CreateView):
    # По умолчанию используется шаблон имени формы: "имя класса" + суффикс "_form".
    # В данном случае - "product_form.html".

    model = Product
    fields = 'name', 'price', 'discount', 'description' # Альтернативно можно указать "form_class". Только что-то одно.
    success_url = reverse_lazy('shopapp:products_list')
    permission_required = 'shopapp.add_product'

    def form_valid(self, form):
        # form.instance - объект модели формы. В нём надо заполнить служебный реквизит, невидимый пользователю.
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    queryset = Product.objects.select_related('created_by')

    # fields = 'name', 'price', 'discount', 'description', 'preview'
    # Форма с возможностью выбора нескольких файлов. Отключена, так как в Django 6 убран множественный выбор файлов.
    form_class = ProductForm

    # По умолчанию суффикс как у CreateView. То есть ищется "product_form".
    # Можно как целиком переопределить имя формы в "template_name", так и ограничиться изменением суффикса:
    template_name_suffix = '_update_form'

    # Чтобы вернуть к details, нужен primary key. При заполнении параметра "success_url" (на "верхнем уровне")
    # недоступен. Поэтому ссылку надо сгенерировать вручную. Здесь уже можно использовать "reverse".
    def get_success_url(self):
        return  reverse(
            'shopapp:product_details',
            kwargs={
                'pk': self.object.pk
            }
        )

    def test_func(self):
        # self.object вызывает ошибку "'ProductUpdateView' object has no attribute 'object'".
        # Поэтому приходится запрашивать отдельно - self.get_object(). Отдельный запрос к базе данных.
        product: Product = self.get_object()

        # Сохраняем объект в self.object ПЕРВЫМ ДЕЛОМ, чтобы запрос к базе данных был только один
        self.object = product

        user = self.request.user

        # Суперпользователю вносить изменения в продукт можно всегда
        if user.is_superuser:
            return True

        # has_perm возвращает True для суперпользователя, но из-за второго условия is_superuser проверен ранее.
        return (
            user.has_perm('shopapp.change_product') # У пользователя есть разрешение на редактирование
            and product.created_by == user # Пользователь — автор продукта, который нужно отредактировать
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )

        return response


class ProductArchiveView(DeleteView):
    model = Product
    success_url = reverse_lazy('shopapp:products_list')

    # По умолчанию используется шаблон имени формы подтверждения действия: "имя класса" + суффикс "_confirm_delete".
    # В данном случае - "product_confirm_delete.html". Для соответствия с функционалом архивации
    # шаблон переименован в "product_confirm_archived.html".
    template_name_suffix = '_confirm_archived'

    def form_valid(self, form):
        # Основна кода взята из родительской реализации.
        # Вместо "self.object.delete()" выполняется архивация "archived = True" и сохранение.
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)


# Не из задания
class ProductsDataExportView(View):
    def get(self, request: HttpRequest) -> JsonResponse:
        cache_key = "products_data_export"
        # Check if the data already exists in the cache
        products_data = cache.get(cache_key)

        # If the data is not already cached, generate it and cache it
        if products_data is None:
            products = Product.objects.order_by('pk').all()
            products_data = [
                {
                    "pk": product.pk,
                    "name": product.name,
                    "price": product.price,
                    "archived": product.archived,
                }
                for product in products
            ]
            cache.set(cache_key, products_data, 300)

        return JsonResponse({"products": products_data})


class ProductViewSet(ModelViewSet):
    """
    Действия над **Product**. Реализует CRUD.
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = SearchFilter, OrderingFilter # Полностью заменяет settings.REST_FRAMEWORK.DEFAULT_FILTER_BACKENDS
    search_fields = 'name', 'description'
    ordering_fields = 'pk', 'name', 'price', 'discount'

    # Не по заданию. Демонстрация настройки короткого описания (summary) для одного метода.
    @extend_schema(summary='Get all Products')
    @method_decorator(cache_page(60 * 2)) # Не по заданию
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # Не по заданию
    @action(methods=["get"], detail=False)
    def download_csv(self, request: Request):
        response = HttpResponse(content_type="text/csv")
        filename = "products-export.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        queryset = self.filter_queryset(self.get_queryset())
        fields = [
            "name",
            "description",
            "price",
            "discount",
        ]
        queryset = queryset.only(*fields)
        writer = DictWriter(response, fieldnames=fields)
        writer.writeheader()

        for product in queryset:
            writer.writerow({
                field: getattr(product, field)
                for field in fields
            })

        return response

    # Не по заданию
    @action(
        detail=False,
        methods=["post"],
        parser_classes=[MultiPartParser],
    )
    def upload_csv(self, request: Request):
        products = save_csv_products(
            request.FILES["file"].file,
            encoding=request.encoding,
        )
        serializer = self.get_serializer(products, many=True)
        return Response(serializer.data)


class LatestProductsFeed(Feed):
    # Метод "item_link" не реализован, так как ссылка получается из "get_absolute_url" модели Product

    title = 'Latest products'
    description = 'Updates on shop latest created products'
    link = reverse_lazy('shopapp:products_list')

    def items(self):
        return (
            Product.objects
            .filter(archived=False)  # Как в списке товаров
            .order_by('-created_at')[:5] # Пять последних созданных. Самые новые. Количество выбрано случайным образом.
        )

    def item_title(self, item: Product):
        return item.name

    def item_description(self, item: Product):
        return item.description[:200] # Количество символов выбрано случайным образом по принципу "name * 2"


# Для теста (не из задания). LoginRequiredMixin - проверка аутентификацию. Обязательно первым.
class OrdersListView(LoginRequiredMixin, ListView):
    # Параметр шаблона "template_name" не указан, так как он назван в соответствии с типовым именем:
    # "имя класса" + суффикс "_list". В данном случае - "order_list.html". В единственном числе, как и имя класса.

    # Параметр имени основного элемента "context_object_name" не указан, так как в шаблоне использовано
    # стандартное имя. Оно формируется также при помощи постфикса - "object_list".

    # Вместо модели можно указать запрос. Причём .all() не нужен.
    queryset = Order.objects.select_related('user').prefetch_related('products')


# Для теста (не из задания). PermissionRequiredMixin - проверка наличия права. Обязательно первым.
class OrdersDetailView(PermissionRequiredMixin, DetailView):
    # Также оставлены типовые имена: шаблон "order_detail.html" и основной элемент "object".

    queryset = Order.objects.select_related('user').prefetch_related('products')
    permission_required = 'shopapp.view_order' # Право, проверяемое в PermissionRequiredMixin


class OrdersCreateView(CreateView):
    model = Order
    fields = 'user', 'promocode', 'delivery_address', 'products'
    success_url = reverse_lazy('shopapp:orders_list')
    template_name = 'shopapp/order_create.html' # Полное переопределение типового имени


class OrdersUpdateView(UpdateView):
    model = Order
    fields = 'user', 'promocode', 'delivery_address', 'products'
    template_name_suffix = '_update' # Частичное переопределение типового имени. Ожидается: "order_update.html".

    def get_success_url(self):
        return  reverse(
            'shopapp:order_details',
            kwargs={
                'pk': self.object.pk
            }
        )


class OrdersDeleteView(DeleteView):
    # По умолчанию используется шаблон имени формы подтверждения действия: "имя класса" + суффикс "_confirm_delete".
    # В данном случае - "order_confirm_delete.html".

    model = Order
    success_url = reverse_lazy('shopapp:orders_list')


class OrdersExportView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def get(self, request: HttpRequest) -> JsonResponse:
        orders = [
            {
                'id': order.pk,
                'delivery_address': order.delivery_address,
                'promocode': order.promocode,
                'user_id': order.user.pk,
                'produsts': [product.pk for product in order.products.all()]
            }
            for order in Order.objects.select_related('user').prefetch_related('products').all()
        ]

        return JsonResponse({'orders': orders})


@extend_schema(description='Действия над **Order**. Реализует CRUD.') # Не по заданию. Демонстрация замены описания.
class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = DjangoFilterBackend, OrderingFilter # Полностью заменяет settings.REST_FRAMEWORK.DEFAULT_FILTER_BACKENDS
    ordering_fields = 'pk', 'delivery_address', 'promocode', 'created_at', 'user'

    # Использовать '__all__' не получится из-за поля receipt, в котором хранится файл (FileField). Будет ошибка:
    # AutoFilterSet resolved field 'receipt' with 'exact' lookup to an unrecognized field type FileField. Try adding an override to 'Meta.filter_overrides'.
    filterset_fields = 'delivery_address', 'promocode', 'created_at', 'user', 'products'


class UserOrdersListView(LoginRequiredMixin, ListView):
    owner: User  # Необязательно. Добавлено для работы контекстной подсказки.

    model = Order

    # Основной шаблон из списка заказов "OrdersListView", так как в задании указано "Обновите шаблон списка заказов".
    # Из-за его использования доступны переходы к другим View. Но с этих View возврат будет на "OrdersListView".
    template_name = 'shopapp/order_list.html'

    def get_queryset(self):
        # Условие задания: "Если пользователь не найден, нужно вернуть ошибку 404"
        self.owner = get_object_or_404(User, pk=self.kwargs['user_id'])

        # Настройки повторяют queryset в "OrdersListView"
        return Order.objects.filter(user=self.owner).select_related('user').prefetch_related('products')

    # IDE по умолчанию предлагает сигнатуру метода:
    # def get_context_data(self, *, object_list = ..., **kwargs) -> dict:
    # Это приведёт к ошибке:
    # 'ellipsis' object is not iterable
    # Исправить можно двумя вариантами:
    # 1. Заменить "..." (ellipsis) на "None".
    # def get_context_data(self, *, object_list = None, **kwargs) -> dict:
    # 2. Вернуть старую сигнатуру. "object_list" уже есть в "kwargs".
    # def get_context_data(self, **kwargs) -> dict:
    # И использовать её при вызове родительского класса:
    # super().get_context_data(**kwargs)
    # Выбран второй вариант из-за итогового меньшего количества кода.
    def get_context_data(self, **kwargs) -> dict:
        context = super().get_context_data(**kwargs)
        context['owner'] = self.owner # К этому моменту уже заполнен в get_queryset
        return context


# В отличие от "UserOrdersListView", проверка авторизации заданием не требовалась.
# Сделано по аналогии с "OrdersExportView". APIView применён, чтобы отследить кэш в Django debug toolbar.
# В качестве альтернативы можно использовать ViewSet из Django Rest Framework:
# class UserOrdersExportView(ListModelMixin, GenericViewSet):
# Но это противоречит условию задания "Используйте view-класс или view-функцию для создания представления".
class UserOrdersExportView(APIView):
    def get(self, request: Request, user_id: int):
        cache_key = f'user_{user_id}_orders_export'

        orders_data = cache.get(cache_key)

        if orders_data is None:
            # Условие задания: "Если пользователь не найден, верните ошибку 404"
            owner = get_object_or_404(User, pk=user_id)

            # Настройки повторяют queryset в "OrdersListView"
            orders = (
                Order.objects
                .filter(user=owner)
                .select_related('user')
                .prefetch_related('products')
                .order_by('pk')  # Условие задания: "Примените сортировку по первичному ключу"
            )

            # "many=True", чтобы указать на преобразование в list
            serialized = OrderSerializer(orders, many=True)
            orders_data = serialized.data

            # Время жизни кэша (2 минуты) выбрано случайным образом.
            cache.set(cache_key, orders_data, 120)

        return Response(orders_data)
