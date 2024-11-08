import json
import sys
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = ['*']

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

config_info = {}
config_path = str(BASE_DIR) + '/config.json'
if os.path.exists(config_path):
    print('\nNo file found => ' + config_path)
    with open(config_path, 'r') as site_config:
        config_info = json.load(site_config)

SERVER_PORT = config_info.get('port') or 8000
SERVER_PORT_STR = ''
if SERVER_PORT:
    SERVER_PORT_STR = ':' + str(SERVER_PORT)

PROTOCOL = 'http'
if config_info.get('https'):
    PROTOCOL = 'https'

server_domain = config_info.get('server_domain')
MAIN_URL = PROTOCOL + '://' + server_domain + SERVER_PORT_STR
LOGIN_URL = MAIN_URL + '/auth/login'
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
IS_LOCALHOST = (len(sys.argv) > 1 and sys.argv[1] == 'runserver')


MFA_PASSKEY_LOGIN_ENABLED = True
MFA_PASSKEY_SIGNUP_ENABLED = True
MFA_SUPPORTED_TYPES = ["webauthn", "totp", "recovery_codes",]
ACCOUNT_LOGIN_BY_CODE_ENABLED = True
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SOCIALACCOUNT_PROVIDERS = {}
INSTALLED_APPS += [
    "auth_signup",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.mfa"
]
MIDDLEWARE += [
    "allauth.account.middleware.AccountMiddleware",
]

def read_social_apps_credentials():
    try:
        social_auth_cred = config_info.get('social_auth')
        return social_auth_cred
    except:
        print('\nError in reading ' + config_path)
        return {}

def add_social_provider_apps():
    provider_candidates = {
        "amazon": {
            "SCOPE": ["profile"],
        },
        "apple": {
            "SCOPE": ["email", "name"],
        },
        "atlassian": {
            "SCOPE": ["read:jira-user"],
        },
        "baidu": {
            "SCOPE": ["basic"],
        },
        "bitbucket_oauth2": {
            "SCOPE": ["account"],
        },
        "dropbox": {
            "SCOPE": ["account_info.read"],
        },
        "dingtalk": {
            "SCOPE": ["user"],
        },
        "edx": {
            "SCOPE": ["email", "profile"],
        },
        "evernote": {
            "SCOPE": ["basic", "notes"],
        },
        "facebook": {
            "SCOPE": ["public_profile"],
            "FIELDS": [
                "id", "email", "name", "first_name", "last_name", "verified", "locale",
                "gender", "link", "picture.type(large)"
            ],
        },
        "figma": {
            "SCOPE": ["file_read"],
        },
        "flickr": {
            "SCOPE": ["read"],
        },
        "github": {
            "SCOPE": ["user", "user:email"],
        },
        "gitlab": {
            "SCOPE": ["read_user"],
        },
        "google": {
            "SCOPE": ["email", "profile"],
            "AUTH_PARAMS": {"access_type": "online"},
        },
        "instagram": {
            "SCOPE": ["user_profile", "user_media"],
        },
        "linkedin_oauth2": {
            "SCOPE": ["r_liteprofile", "r_emailaddress"],
        },
        "microsoft": {
            "SCOPE": ["openid", "email", "profile", "User.Read"],
        },
        "nextcloud": {
            "SCOPE": ["read"],
        },
        "paypal": {
            "SCOPE": ["profile"],
        },
        "pinterest": {
            "SCOPE": ["read_public"],
        },
        "reddit": {
            "SCOPE": ["identity", "read", "submit"],
        },
        "shopify": {
            "SCOPE": ["read_products"],
        },
        "slack": {
            "SCOPE": ["users:read"],
        },
        "snapchat": {
            "SCOPE": ["snaps.read"],
        },
        "soundcloud": {
            "SCOPE": ["non-expiring"],
        },
        "stackexchange": {
            "SCOPE": ["no-expiry"],
        },
        "telegram": {
            "SCOPE": ["user"],
        },
        "tiktok": {
            "SCOPE": ["user.info.basic"],
        },
        "twitter_oauth2": {
            "SCOPE": ["read"],
        },
        "vimeo": {
            "SCOPE": ["public"],
        },
        "weibo": {
            "SCOPE": ["all"],
        },
        "xing": {
            "SCOPE": ["read_profiles"],
        },
    }
    social_auth_cred = read_social_apps_credentials()
    for social_provider in social_auth_cred:
        config_obj = social_auth_cred[social_provider]
        if not provider_candidates.get(social_provider):
            continue
        if not config_obj.get('key') or config_obj.get('key') == 'xx':
            print('No key provided for ' + social_provider)
            continue
        provider_candidates[social_provider]['APP'] = {
            "client_id": config_obj['key'],
            "secret": config_obj['secret'],
        }
        SOCIALACCOUNT_PROVIDERS[social_provider] = provider_candidates[social_provider]
        INSTALLED_APPS.append("allauth.socialaccount.providers." + social_provider)

add_social_provider_apps()
INSTALLED_APPS.append("allauth.usersessions")