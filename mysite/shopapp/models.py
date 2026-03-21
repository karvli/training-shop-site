from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def product_preview_directory_path(instance: "Product", filename: str) -> str:
    return "products/product_{pk}/preview/{filename}".format(
        pk=instance.pk,
        filename=filename,
    )


class Product(models.Model):
    """
    Модель **Product** - товар, продаваемый в интернет-магазине.
    """

    class Meta:
        ordering = ["name", "price"]
        verbose_name = _('Product')
        verbose_name_plural = _('Products')

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True) # Без "null = False", так как по умолчанию и так "не null"
    created_at = models.DateTimeField(auto_now_add=True) # Заполняется только при создании текущими датой и временем
    archived = models.BooleanField(default=False)  # Архивный - "Не использовать", "Нет в наличии"
    preview = models.ImageField(null=True, blank=True, upload_to=product_preview_directory_path)

    # 6 знаков целой части и 2 - дробной
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])

    # default=0, чтобы не передавать значение (иначе ошибка Null)
    discount = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])

    # Связь "многие-к-одному". У одного пользователя может быть много продуктов.
    created_by = models.ForeignKey(
        User,
        null=True, # Могут быть продукты, созданные "служебным" функционалом. Редактирование только администратором.
        on_delete=models.SET_NULL, # До назначения нового пользователя продукт становится "служебным".
    )

    # Для удобства. В задании не требовалось.
    def __str__(self):
        return f'Product (pk={self.pk}, name={self.name!r})'

    # Автоматически используется в методах "item_link" у Feed (RSS) и Sitemap
    def get_absolute_url(self):
        return reverse('shopapp:product_details', kwargs={'pk': self.pk})


# Не из задания
def product_images_directory_path(instance: "ProductImage", filename: str) -> str:
    return "products/product_{pk}/images/{filename}".format(
        pk=instance.product.pk,
        filename=filename,
    )


# Не из задания
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to=product_images_directory_path)
    description = models.CharField(max_length=200, null=False, blank=True)


class Order(models.Model):
    """
    Модель **Order** - заказ клиента :model:`auth.User` интернет-магазина.
    Заказ состоит из нескольких товаров :model:`shopapp.Product`.
    """

    class Meta:
        verbose_name = _('Order')
        verbose_name_plural = _('Orders')

    delivery_address = models.TextField(blank=True)
    promocode = models.CharField(max_length=10, blank=True)
    created_at = models.DateTimeField(auto_now_add=True) # Заполняется только при создании текущими датой и временем
    user = models.ForeignKey(User, on_delete=models.PROTECT) # on_delete, чтобы не удалило пользователей, у которых есть заказы
    products = models.ManyToManyField(Product, related_name='orders') # related_name - название в классе Product
    receipt = models.FileField(null=True, upload_to='orders/receipts/') # Доступно только в /admin