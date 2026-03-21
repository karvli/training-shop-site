from django.db import models
from django.urls import reverse


class Author(models.Model):
    name = models.CharField(max_length=100)
    bio =  models.TextField(blank=True) # По умолчанию может быть пустой строкой, раз в задании "МОЖЕТ содержать"

    def __str__(self):
        return self.name


class Category(models.Model):
    name =  models.CharField(max_length=40)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name =  models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True) # По умолчанию может быть пустой строкой, раз в задании "МОЖЕТ содержать"
    pub_date = models.DateTimeField(null=True, blank=True) # По аналогии с примером из видео курса
    author = models.ForeignKey(Author, on_delete=models.CASCADE) # Если автора нет, его статьи нужно удалить
    category = models.ForeignKey(Category, on_delete=models.CASCADE) # Если категории нет, её статьи нужно удалить
    tags = models.ManyToManyField(Tag, related_name='articles', blank=True) # В задании не указано, но, по идее, тегов может и не быть

    def __str__(self):
        return f'{self.title!r} from {self.pub_date}'

    def get_absolute_url(self):
        return reverse("blogapp:article", kwargs={"pk": self.pk})