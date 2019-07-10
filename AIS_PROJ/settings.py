import os
import dropbox

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'l)!f_(du!#14^yq3wb5p!mep1kcysy-v^c1d=9fvuz(y&nvu26'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['18.214.129.131', '127.0.0.1', '0.0.0.0', 'facespace.ai']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'athletes',
    'events',
    'userprofile',
    'storages',
    'import_export',
    'rest_framework',
    'rest_framework_datatables',
    'client',
    'djrill',

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'AIS_PROJ.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'AIS_PROJ.wsgi.application'

"""
# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#database
DATABASES = {
'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'aispostgres',
    'USER': 'asif4347',
    'PASSWORD': 'asif4347',
    'HOST': 'aispostgres.c44rartggmzf.us-east-1.rds.amazonaws.com',
    'PORT': '5432',
    }
}
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'asif4347',
        'USER': 'asif4347',
        'PASSWORD': 'asif4347',
        'HOST': 'asif4347.c44rartggmzf.us-east-1.rds.amazonaws.com',
        'PORT': '3306',
    }
}
"""

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_datatables.renderers.DatatablesRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'rest_framework_datatables.filters.DatatablesFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework_datatables.pagination.DatatablesPageNumberPagination',
    'PAGE_SIZE': 20,
}

# Settings Variables
IMPORT_EXPORT_USE_TRANSACTIONS = True
LOGIN_REDIRECT_URL = '/events'
STATIC_URL = '/static/'
PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))
STATICFILES_DIRS = [
    '/userprofile/static'
]
STATIC_ROOT = PROJECT_PATH + '/static/'

MEDIA_ROOT = PROJECT_PATH + '/media/'
MEDIA_URL = '/media/'
# DROPBOX_OAUTH2_TOKEN='rBv6isYi_-AAAAAAAAABqZdoOiraXozqrgH6SKyGeDWO-99RMxjMirkdEHiOSpj6'
DROPBOX_OAUTH2_TOKEN = 'boCgY96xgscAAAAAAALZDwAlYCt64RgdREEAlvjrAYJaG0hpVO-nSFaskKuD8tp5'

DROPBOX_PATH = '/ai application/'

AWS_S3_ACCESS_KEY_ID = 'AKIA6DKNBJPSZDE7UUUH'  # enter your access key id
AWS_S3_SECRET_ACCESS_KEY = 'iEdfR4BByrOBK5EqlTc3XD5XUZCRQWPE2uD/rPBu'  # enter your secret access key
AWS_STORAGE_BUCKET_NAME = 'ais-django'
AWS_ACCESS_KEY_ID = AWS_S3_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = AWS_S3_SECRET_ACCESS_KEY
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_POSTGRESS_ENDPOINT = 'ais.c44rartggmzf.us-east-1.rds.amazonaws.com'
AWS_POSTGRESS_USER = 'Novatore'
AWS_POSTGRESS_PASS = 'Novatore'
AWS_POSTGRESS_PORT = '5432'
# DEFAULT_FILE_STORAGE='AIS_PROJ.backend_storages.MediaStorage'

# EMAIL_USE_TLS = True
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_HOST_USER = 'facesapceai@gmail.com'
# EMAIL_HOST_USER = 'hello@facespace.ai'
# EMAIL_HOST_PASSWORD = 'FaceSpace.AI007'
# EMAIL_PORT = 587
#
# from_email = 'facesapceai@gmail.com'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.mandrillapp.com'
EMAIL_HOST_USER = 'hello@facespace.ai'
EMAIL_HOST_PASSWORD = 'FaceSpace.AI007'
EMAIL_PORT = 587

from_email = 'hello@facespace.ai'

DATA_UPLOAD_MAX_NUMBER_FIELDS = 10000
MANDRILL_API_KEY = "1lYy4ctHFGWrtIa5wszv5w"
EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"
DEFAULT_FROM_EMAIL = 'hello@facespace.ai'
