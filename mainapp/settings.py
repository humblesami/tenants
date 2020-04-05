import json
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
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = "/media/"
TENANT_APPS_DIR = os.path.join(PROJECT_DIR, os.pardir)
sys.path.insert(0, TENANT_APPS_DIR)

config_path = (BASE_DIR+'/config.json')
config_path = config_path.replace('\\/', '\\')
config_path = config_path.replace('//', '/')

MAX_UPLOAD_SIZE = "5242880"

DATABASES = {
    'default': {}
}

ip2location = {}
server_base_url = ''
SOCKET_SERVER_URL = ''
base_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = base_dir.replace('mainapp', '')


config_info = {}
with open(config_path, 'r') as site_config:
    config_info = json.load(site_config)
    DATABASES['default'] = config_info['default']
    SOCKET_SERVER_URL = config_info['socket_url']
    server_base_url = config_info['server_base_url']
    AUTH_SERVER_URL = config_info['auth_server_url']
    ip2location = config_info["ip2location"]["active"]

EMAIL_HOST = config_info['email']['EMAIL_HOST']
EMAIL_PORT = config_info['email']['EMAIL_PORT']
EMAIL_HOST_USER = config_info['email']['EMAIL_HOST_USER']
EMAIL_HOST_PASSWORD = config_info['email']['EMAIL_HOST_PASSWORD']
EMAIL_USE_TLS = True


TIME_ZONE = 'America/Chicago'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True
MEDIA_ROOT = ''
MEDIA_URL = ''


PROJECT_ROOT = os.path.normpath(os.path.dirname(__file__))
# CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    'localhost:4200',
    '127.0.0.1:4200',
)


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated', )
}

MIDDLEWARE = (
    'mainapp.middleware.TenantMiddleware',
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
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(PROJECT_ROOT, '..', 'mainapp/templates'),
            os.path.join(PROJECT_ROOT, '..', 'ngapp/templates'),
            os.path.join(PROJECT_ROOT, '..', 'emailthread/templates'),
            # os.path.join(PROJECT_ROOT, '..', 'authsignup/templates'),
            os.path.join(PROJECT_ROOT, '..', 'temp/templates'),
            os.path.join(PROJECT_ROOT, '..', 'documents/templates'),
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
    'django.contrib.contenttypes',
    'django.contrib.auth',
    # 'django.contrib.admin',
    'mainapp.apps.CustomAdminConfig',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'emailthread',
    'django_tenants',
    'customers',
    'website',
)

TENANT_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.auth',
    # 'django.contrib.admin',
    'mainapp.apps.CustomAdminConfig',
    'django.contrib.sessions',
    'django.contrib.messages',
    'corsheaders',
    'tenant_only',
    'bootstrapform',

    'rest_framework',
    'rest_framework.authtoken',
    'my_admin',
    'authcode',
    'authsignup',
    'ngapp',
    'documents',
    'chat',
    'nested_admin',
    'restoken',
)
INSTALLED_APPS = list(set(TENANT_APPS + SHARED_APPS))

STATIC_URL = '/static/'
PROJECT_ROOT = os.path.normpath(os.path.dirname(__file__))
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, '..', 'static'),
)

SECRET_KEY = 'as-%*_93v=r5*p_7cu8-%o6b&x^g+q$#*e*fl)k)x0-t=%q0qa'

ROOT_URLCONF = 'mainapp.urls_tenants'
PUBLIC_SCHEMA_URLCONF = 'mainapp.urls_public'
WSGI_APPLICATION = 'mainapp.wsgi.application'

TENANT_MODEL = "customers.Client"  # app.Model
TENANT_DOMAIN_MODEL = "customers.Domain"  # app.Model

SERVER_PORT = config_info['port']
SERVER_PORT_STR = ''
if SERVER_PORT:
    SERVER_PORT_STR = ':' + str(SERVER_PORT)

PROTOCOL = 'http'
if config_info['https']:
    PROTOCOL = 'https'

server_domain = config_info['server_domain']
MAIN_URL = PROTOCOL + '://' + server_domain + SERVER_PORT_STR
LOGIN_URL = MAIN_URL + '/accounts/login'

PUBLIC_TENANT = None

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