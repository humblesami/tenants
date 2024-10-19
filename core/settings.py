from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = []

"""These app's data are stored on the public schema"""
SHARED_APPS = [
    'dj_utils',
    'django_tenants',  # mandatory
    'companies',  # you must list the app where your tenant model resides in
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ckeditor',
    'ckeditor_uploader',
    'restoken',
]
"""These app's data are stored on their specific schemas"""
TENANT_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.messages',
    'blog'
]

INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

MIDDLEWARE = [
    'django_tenants.middleware.main.TenantMainMiddleware',
    # custom tenant middleware
    'core.middleware.TenantMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TENANT_MODEL = "companies.ClientTenant"
TENANT_DOMAIN_MODEL = "companies.Domain"
ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                # django_tenant finds tenant upon request
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

# DATABASE ROUTER
DATABASE_ROUTERS = (
    'django_tenants.routers.TenantSyncRouter',
)

AUTH_PASSWORD_VALIDATORS = [{
    'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
}, {
    'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
}, {
    'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
}, {
    'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
}]


LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

import os
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
MEDIA_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_ROOT = os.path.join(BASE_DIR, 'media')
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'


SECRET_KEY = 'django-insecure-u=)nti=7vv^gf+ma6%3=3wr(o3_ja@4i&slm35y3w(w_06bad5'
DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': 't1',
        'USER': 'odoo',
        'PASSWORD': '123',
    }
}

CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
    },
}

config_info= {'port': 8000, 'server_domain': 'localhost'}
SERVER_PORT = config_info['port']
SERVER_PORT_STR = ''
if SERVER_PORT:
    SERVER_PORT_STR = ':' + str(SERVER_PORT)

PROTOCOL = 'http'
if config_info.get('https'):
    PROTOCOL = 'https'

server_domain = config_info.get('server_domain')
MAIN_URL = PROTOCOL + '://' + server_domain + SERVER_PORT_STR
LOGIN_URL = MAIN_URL + '/accounts/login'
SOCKET_SERVER_URL = 'http://localhost:3000'
AUTH_PASSWORD_VALIDATORS = []
PUBLIC_DOMAIN = config_info.get('public_host_name') or 'localhost'
IP2LOC = {
    "base_url": "http://api.ipstack.com/",
    "params": {
        "access_key":"94bfb283cce53facd307167d1596b8c8"
    },
    "prefix": "http://api.ipstack.com/",
    "postfix":"?access_key=94bfb283cce53facd307167d1596b8c8"
}