from django.contrib import admin

from blogapp.models import Author, Category, Tag, Article


# Не по заданию. Для возможности заполнения через интерфейс.
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = 'pk', 'name'
    list_display_links = 'pk', 'name'


# Не по заданию. Для возможности заполнения через интерфейс.
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = 'pk', 'name'
    list_display_links = 'pk', 'name'


# Не по заданию. Для возможности заполнения через интерфейс.
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = 'pk', 'name'
    list_display_links = 'pk', 'name'


# Не по заданию. Для возможности заполнения через интерфейс.
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = 'pk', 'title', 'pub_date', 'author', 'category'
    list_display_links = 'pk', 'title'
