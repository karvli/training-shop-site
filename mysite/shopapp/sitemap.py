from django.contrib.sitemaps import Sitemap

from shopapp.models import Product


class ShopSitemap(Sitemap):
    # Метод "item_link" не реализован, так как ссылка получается из "get_absolute_url" модели Product

    changefreq = 'never' # Как часто меняется информация - "никогда"
    priority = 0.5 # Приоритет страницы, где "1" - самая главная (приоритетная)

    def items(self):
        return Product.objects.all()

    def lastmod(self, obj: Product):
        return obj.created_at