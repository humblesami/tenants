from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings


def home(request):
    return HttpResponse('<h2>Home</h2>')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('blog/', include('blog.urls', namespace='blog')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

