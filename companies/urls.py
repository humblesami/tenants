from django.urls import path
from django.contrib.auth.decorators import user_passes_test

urlpatterns = [
    # path('new', user_passes_test(lambda u: u.is_superuser)(Create.as_view())),
]