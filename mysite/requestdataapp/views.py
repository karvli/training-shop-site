from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

def file_upload(request: HttpRequest) -> HttpResponse:
    context = {
        'is_big_file_error': False # Регулирует отображение ошибки размера файла в шаблоне
    }
    status = 200

    if request.method == 'POST':
        file = request.FILES.get('selected_file')

        if file is not None:
            max_size = 1048576  # 1 мегабайт в байтах
            if file.size <= max_size:
                # location - найден в документации. Определяет положение относительно корня проекта.
                # Таким образом файлы буду сохраняться в каталог 'uploaded_files', расположенный в "верхнем" mysite.
                fs = FileSystemStorage(location='uploaded_files')
                filename = fs.save(file.name, file)
                print('Saved file', filename)
                print(file.size)
            else:
                context['is_big_file_error'] = True
                status = 413 # "Request Entity Too Large", "Запрос слишком велик"

    return render(request, "requestdataapp/file-upload.html", context, status=status)