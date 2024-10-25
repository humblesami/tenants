from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings


def home(request):
    return HttpResponse('<h2>Home</h2>')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authsignup.urls')),
    path('blog/', include('blog.urls')),
    path('', home),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

