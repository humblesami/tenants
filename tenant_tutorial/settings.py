# Django settings for tenant_tutorial project.
import os
import sys

DEBUG = True
ALLOWED_HOSTS = ['*']

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, os.pardir)
TENANT_APPS_DIR = os.path.join(PROJECT_DIR, os.pardir)
sys.path.insert(0, TENANT_APPS_DIR)

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True
MEDIA_ROOT = ''
MEDIA_URL = ''
PROJECT_ROOT = os.path.normpath(os.path.dirname(__file__))
STATIC_URL = '/static/'
TENANT_MODEL = "customers.Client"
TENANT_DOMAIN_MODEL = "customers.Domain"
TENANT_USERS_DOMAIN = "localhost"
AUTH_USER_MODEL = 'users.TenantUser'
SERVER_PORT = 8001
SERVER_PORT_STR = ':' + str(SERVER_PORT)

DEFAULT_FILE_STORAGE = "django_tenants.files.storage.TenantFileSystemStorage"
MULTITENANT_RELATIVE_MEDIA_ROOT = "uploaded_files"
STRIPE_SECRET_KEY = 'sk_test_iXAXCCa4TeYZdfjSl0GfYjic001xWmMuDu'
STRIPE_PUBLISHABLE_KEY = 'pk_test_b0jaMPWTlpMV6c7HXNovbMuh00iATzbXHH'
DJSTRIPE_WEBHOOK_SECRET = "whsec_GZS0YLboypzBblOZoyY121KWuxzjpwdF"
ROOT_URLCONF = 'tenant_tutorial.urls_tenants'
PUBLIC_SCHEMA_URLCONF = 'tenant_tutorial.urls_public'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'as-%*_93v=r5*p_7cu8-%o6b&x^g+q$#*e*fl)k)x0-t=%q0qa'
TEST_RUNNER = 'django.test.runner.DiscoverRunner'
WSGI_APPLICATION = 'tenant_tutorial.wsgi.application'
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'
# SESSION_COOKIE_DOMAIN = '.' + TENANT_USERS_DOMAIN

STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, '..', 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# List of callables that know how to import templates from various sources.
DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)

DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': 'tt',
        'USER': 'odoo',
        'PASSWORD': '123',
    }
}

MIDDLEWARE = (
    'tenant_tutorial.middleware.TenantMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates')

        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

AUTHENTICATION_BACKENDS = (
    'tenant_users.permissions.backend.UserBackend',
)

SHARED_APPS = (
    'django_tenants',    
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'tenant_users.permissions',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.admin',
    'tenant_users.tenants',
    'customers',
    'users',
    'my_stripe'
)

TENANT_APPS = (    
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'tenant_users.permissions',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.admin',
    'tenant_only',
)

INSTALLED_APPS = list(set(TENANT_APPS + SHARED_APPS))