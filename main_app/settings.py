import sys
import os

DEBUG = True
ALLOWED_HOSTS = ['*']
ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)
MANAGERS = ADMINS

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_DIR = os.path.join(BASE_DIR, os.pardir)

TENANT_APPS_DIR = os.path.join(PROJECT_DIR, os.pardir)
sys.path.insert(0, TENANT_APPS_DIR)

DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': 'tt',
        'USER': 'odoo',
        'PASSWORD': '123',
    }
}

TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True
MEDIA_ROOT = ''
MEDIA_URL = ''

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


MIDDLEWARE = (
    'main_app.middleware.TenantMiddleware',
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

SHARED_APPS = (
    'django_tenants',
    'customers',
    'website',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
)

TENANT_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.messages',
    'tenant_only',
)
INSTALLED_APPS = list(set(TENANT_APPS + SHARED_APPS))

STATIC_URL = '/static/'
PROJECT_ROOT = os.path.normpath(os.path.dirname(__file__))
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, '..', 'static'),
)

SECRET_KEY = 'as-%*_93v=r5*p_7cu8-%o6b&x^g+q$#*e*fl)k)x0-t=%q0qa'

ROOT_URLCONF = 'main_app.urls_tenants'
PUBLIC_SCHEMA_URLCONF = 'main_app.urls_public'
WSGI_APPLICATION = 'main_app.wsgi.application'

TENANT_MODEL = "customers.Client"  # app.Model
TENANT_DOMAIN_MODEL = "customers.Domain"  # app.Model
TENANT_DOMAIN = 'localhost'
SERVER_PORT = 8001
SERVER_PORT_STR = ''
if SERVER_PORT:
    SERVER_PORT_STR = ':' + str(SERVER_PORT)
DOMAIN_NAME = TENANT_DOMAIN
MAIN_URL = DOMAIN_NAME + SERVER_PORT_STR
# SESSION_COOKIE_NAME = 'fdfdsedfsoodsd'
# SESSION_COOKIE_DOMAIN = '.' + TENANT_DOMAIN + SERVER_PORT_STR
LOGIN_URL = '/accounts/login'

TEST_RUNNER = 'django.test.runner.DiscoverRunner'
DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)


DEFAULT_FILE_STORAGE = "django_tenants.files.storage.TenantFileSystemStorage"
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

DEFAULT_FILE_STORAGE = "django_tenants.files.storage.TenantFileSystemStorage"
MULTITENANT_RELATIVE_MEDIA_ROOT = "uploaded_files"


STRIPE_SECRET_KEY = 'sk_test_iXAXCCa4TeYZdfjSl0GfYjic001xWmMuDu'
STRIPE_PUBLISHABLE_KEY = 'pk_test_b0jaMPWTlpMV6c7HXNovbMuh00iATzbXHH'
DJSTRIPE_WEBHOOK_SECRET = "whsec_GZS0YLboypzBblOZoyY121KWuxzjpwdF"