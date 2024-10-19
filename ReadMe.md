## Build A SAAS With Django, Simplest on Github till now

### Introduction

-> What is a Saas and How to build a Saas

-> Clone Project files or use your project files

```bash
# Make sure you have git installed
git clone https://github.com/Academy-Omen/django-blogx.git
# clone with SSH
git clone git@github.com:Academy-Omen/django-blogx.git
```

-> Create Virtual environment

-> Activate environment

-> Install Requirements

```bash
pip install -r requirements.txt
```

-> Make sure project is running

```bash
python manage.py runserver
```

-> Install django tenants

```bash
# drops db with name t1 (if exists) then creates and migrations
python manage.py reset -hard
```

-> Setup Initial User, Tenant and Admin

```bash
python manage.py runserver
```

Open /admin
create a tenant
remember the domain
client1.localhost
it will auto create a user  admin with password 123
open http://client1.localhot:8000/admin

##### For more information check the [django tenant docs](https://django-tenants.readthedocs.io/)
