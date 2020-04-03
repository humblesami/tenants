from django.urls import path

from . import views


app_name = 'documents'
urlpatterns = [
    path('docs/upload-files', views.upload_files, name = 'index'),
    path('annotation/reset', views.reset_annotations, name = 'index'),
    path('docs/upload-single-file', views.upload_single_file, name = 'single_file'),
    path('docs/upload-single-image-file', views.upload_single_image_file, name = 'single_image_file'),
]