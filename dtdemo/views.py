from django.http import HttpResponse
from django.shortcuts import render
from customer.models import Client, Domain


def root_view(request):
    return HttpResponse('Hoello Root')

def create_tenant(request):
    # create your public tenant
    return render(request, 'index.html', {'message': 'yes'})
    sub_domain = request.GET['name']
    tenant = Client(schema_name=sub_domain,
                    name='My First Tenant',
                    paid_until='2020-12-05',
                    on_trial=True)
    existing = Client.objects.filter(schema_name = tenant.schema_name).first()
    if existing:
        return render(request, 'index.html', {'message': tenant.schema_name+ 'already exists'})
    tenant.save()

    # Add one or more domains for the tenant
    domain = Domain()
    my_domain = 'dtdemo.local'
    domain.domain = tenant.schema_name +'.'+ my_domain
    domain.tenant = tenant
    domain.is_primary = True
    domain.save()
    return render(request, 'index.html', {'message': 'Created'})