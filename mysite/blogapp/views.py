from django.contrib.syndication.views import Feed
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DetailView

from blogapp.models import Article


class ArticlesListView(ListView):
    # Параметр шаблона "template_name" не указан, так как он назван в соответствии с типовым именем:
    # "имя класса" + суффикс "_list". В данном случае - "article_list.html".

    queryset = (
        Article.objects
        .select_related('author', 'category')
        .prefetch_related('tags')

        # В шаблоне поля author, category, tags выводятся без ".name".
        # В __str__ используется name, поэтому их не исключаем из запроса данных.
        # Если исключить, то при отображении выполнится отдельный запрос name.
        # Исключение неиспользуемого служебного поля 'author__id' не требуется. Оно всё равно добавится в запрос.
        .defer('content', 'author__bio')

        # Не по заданию. По аналогии из примера курса.
        .filter(pub_date__isnull=False)
        .order_by('-pub_date') # Для удобства сначала самые актуальные (новые) статьи
    )


class ArticleCreateView(CreateView):
    model = Article
    fields = '__all__'
    success_url = reverse_lazy('blogapp:articles')
    template_name_suffix = '_create' # Частичное переопределение имени. Ожидается: "article_create.html".


class ArticleUpdateView(UpdateView):
    model = Article
    fields = '__all__'
    success_url = reverse_lazy('blogapp:articles')
    template_name_suffix = '_update' # Частичное переопределение имени. Ожидается: "article_update.html".


# Не из задания
class ArticleDetailView(DetailView):
    model = Article


# Не из задания
class LatestArticlesFeed(Feed):
    title = "Blog articles (latest)"
    description = "Updates on changes and addition blog articles"
    link = reverse_lazy("blogapp:articles")

    def items(self):
        return (
            Article.objects
            .filter(pub_date__isnull=False)
            .order_by("-pub_date")[:5]
        )

    def item_title(self, item: Article):
        return item.title

    def item_description(self, item: Article):
        return item.content[:200]
