from django.urls import path
from customers.views import Delete, Create, MyCompanies, CompanyList
from django.contrib.auth.decorators import user_passes_test

urlpatterns = [
    # path('new', user_passes_test(lambda u: u.is_superuser)(Create.as_view())),
    path('delete', user_passes_test(lambda u: u.is_superuser)(Delete.as_view())),
    # path('', user_passes_test(lambda u: u.is_superuser)(TenantView.as_view())),
    path('my-companies',(MyCompanies.as_view())),
    path('list',(CompanyList.as_view())),
]