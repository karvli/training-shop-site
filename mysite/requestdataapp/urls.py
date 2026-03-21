from django.urls import path

from requestdataapp.views import file_upload

app_name = 'requestdataapp'

urlpatterns = [
    path("upload/", file_upload, name='file-upload'),
]