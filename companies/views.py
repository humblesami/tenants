# from django.views import View
# from django.conf import settings
# from django.http import HttpResponse
# from django.contrib.auth.models import User
# from django.db import transaction, connection
# from django.views.generic import TemplateView
# from django_tenants.utils import get_tenant_model
# from django.contrib.contenttypes.models import ContentType
#
# from dj_utils.py import LogUtils
# from .payments.payment_models import PaymentInProgress
#
#
#
# class CheckForExisting(View):
#     def get(self, request):
#         request = self.request
#         name = request.GET['name']
#         tenant_model = get_tenant_model()
#         obj = tenant_model.objects.filter(schema_name=name)
#         result = {}
#         if obj:
#             result = 'Already Exist'
#         else:
#             obj = PaymentInProgress.objects.filter(company=name)
#             if obj:
#                 result = 'Already Exist'
#             else:
#                 result = 'done'
#         return HttpResponse(result)
#
#
# class Create(TemplateView):
#
#     template_name = "companies/tenant_list.html"
#
#     def get_context_data(self, **kwargs):
#         context = {}
#         try:
#             tenant_name = self.request.POST.get('name')
#             if not tenant_name:
#                 tenant_name = self.request.GET.get('name')
#             if not tenant_name:
#                 context ['error'] = 'No name provided'
#                 return context
#             res = create_tenant(tenant_name, self.request)
#             if res != 'done':
#                 context['error'] = res
#             else:
#                 context['message'] = 'Successfully created '+tenant_name
#         except:
#             context['error'] = LogUtils.get_error_message()
#         context['list'] = get_customer_list(self.request.user)
#         context['port'] = settings.SERVER_PORT_STR
#         return context
#
#
# class Delete(TemplateView):
#
#     template_name = "companies/tenant_list.html"
#
#     def get_context_data(self, **kwargs):
#         res = 'Unknown status'
#         customer_id = self.request.GET['id']
#         context = {}
#         try:
#             TenantModel = get_tenant_model()
#             TenantModel.objects.get(pk = customer_id).delete_tenant()
#             context = {'list': get_customer_list(self.request.user)}
#         except:
#             res = LogUtils.get_error_message()
#             context = {'error': res, 'list': get_customer_list(self.request.user)}
#         context['port'] = settings.SERVER_PORT_STR
#         return context
#
#
# class CompanyList(TemplateView):
#     template_name = "companies/clients.html"
#     def get_context_data(self, **kwargs):
#
#         context = {'clients': get_customer_list(self.request.user)}
#         context['port'] = settings.SERVER_PORT_STR
#         return context
#
# def get_customer_list(user):
#     tenants_list = []
#     if user.is_superuser:
#         tenant_model = get_tenant_model()
#         tenants_list = tenant_model.objects.all()
#         tenants_list = tenants_list.prefetch_related('domains').all()
#         tenants_list = list(tenants_list.values('id', 'schema_name', 'domain_name'))
#     return tenants_list
#
#
#
# def create_tenant(t_name, request):
#     res = 'Unknown issue'
#     try:
#         tenant_model = get_tenant_model()
#         with transaction.atomic():
#             if not tenant_model.objects.filter(schema_name=t_name):
#
#                 owner = User.objects.create(username='admin@'+t_name, is_active=True, is_staff=True)
#                 owner.set_password('123')
#                 owner.save()
#
#                 domain_name = t_name + '.' + settings.server_domain
#                 company = tenant_model(schema_name=t_name, name=t_name, owner_id=owner.id, domain_name=domain_name)
#                 company.save()
#                 company.users.add(owner)
#
#                 request.tenant = company
#                 connection.set_tenant(request.tenant, False)
#                 ContentType.objects.clear_cache()
#
#                 owner = User.objects.create(username='admin@' + t_name, is_superuser=True, is_staff=True, is_active=True)
#                 owner.set_password('123')
#                 owner.save()
#
#                 company = tenant_model.objects.get(schema_name='public')
#                 request.tenant = company
#                 connection.set_tenant(request.tenant, False)
#                 ContentType.objects.clear_cache()
#
#                 res = 'done'
#             else:
#                 res = 'Client with id' + t_name + ' already exists'
#     except:
#         res = LogUtils.get_error_message()
#     return res
#
