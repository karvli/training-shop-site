from django.urls import path

from blogapp.views import ArticlesListView, ArticleCreateView, ArticleUpdateView, ArticleDetailView, LatestArticlesFeed

app_name = 'blogapp'

urlpatterns = [
    path('articles/', ArticlesListView.as_view(), name='articles'),
    path('articles/create/', ArticleCreateView.as_view(), name='article_create'),
    path("articles/<int:pk>/", ArticleDetailView.as_view(), name="article"),
    path('articles/<int:pk>/update/', ArticleUpdateView.as_view(), name='article_update'),
    path("articles/latest/feed/", LatestArticlesFeed(), name="articles-feed"),
]