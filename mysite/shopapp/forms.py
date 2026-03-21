from django import forms

from shopapp.models import Product


# Не из задания.
# В Django 4 код множественного выбора файлов работал. Но в Django 6 выдаёт ошибку:
# ValueError: ClearableFileInput doesn't support uploading multiple files.
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = 'name', 'price', 'discount', 'description', 'preview'

    # В Django 4 код множественного выбора файлов работал. Но в Django 6 выдаёт ошибку:
    # ValueError: ClearableFileInput doesn't support uploading multiple files.
    # Обходного решения нет. Только разработка своего класса, где будет переопределён признак множественного выбора.
    # Решено отключить. Загрузить несколько картинок можно в /admin.
    # images = forms.ImageField(
    #     widget=forms.ClearableFileInput(attrs={"multiple": True}),
    # )


# Универсальное имя, чтобы иметь возможность использовать повторно для загрузки чего-то, кроме Order
class CSVImportForm(forms.Form):
    csv_file = forms.FileField()
