from django.urls import path, include
from django.views.decorators.cache import cache_page
from rest_framework.routers import DefaultRouter

from .views import (
    shop_index,
    GroupsListView,
    ProductListView,
    ProductDetailsView,
    OrdersListView,
    OrdersDetailView,
    ProductCreateView,
    ProductUpdateView,
    OrdersCreateView,
    OrdersUpdateView,
    ProductArchiveView,
    OrdersDeleteView,
    OrdersExportView,
    ProductsDataExportView,
    ProductViewSet,
    OrderViewSet,
    LatestProductsFeed,
    UserOrdersListView,
    UserOrdersExportView,
)

app_name = 'shopapp'

routers = DefaultRouter()
routers.register('products', ProductViewSet)
routers.register('orders', OrderViewSet)

urlpatterns = [
    path("", shop_index, name='index'),
    path("api/", include(routers.urls)),

    # Не по заданию. Альтернативное кэширование целиком для View.
    # Оригинал без кэширования:
    # path("groups/", GroupsListView.as_view(), name="groups_list"),
    path("groups/", cache_page(60 * 3)(GroupsListView.as_view()), name="groups_list"),

    path("products/", ProductListView.as_view(), name='products_list'),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path("products/export/", ProductsDataExportView.as_view(), name="products-export"),
    path("products/<int:pk>/", ProductDetailsView.as_view(), name='product_details'),
    path("products/<int:pk>/update/", ProductUpdateView.as_view(), name='product_update'),
    path("products/<int:pk>/archive", ProductArchiveView.as_view(), name='product_archive'),
    path("products/latest/feed/", LatestProductsFeed(), name='products_feed'),

    path("orders/", OrdersListView.as_view(), name='orders_list'),
    path("orders/export/", OrdersExportView.as_view(), name='orders_export'),
    path("orders/create/", OrdersCreateView.as_view(), name="order_create"),
    path("orders/<int:pk>/", OrdersDetailView.as_view(), name='order_details'),
    path("orders/<int:pk>/update", OrdersUpdateView.as_view(), name='order_update'),
    path("orders/<int:pk>/delete", OrdersDeleteView.as_view(), name='order_delete'),

    path("users/<int:user_id>/orders/", UserOrdersListView.as_view(), name='user_orders_list'),
    path("users/<int:user_id>/orders/export/", UserOrdersExportView.as_view(), name='user_orders_export'),
]