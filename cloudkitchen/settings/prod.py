from cloudkitchen.settings.base import *

DEBUG = False

ALLOWED_HOSTS = ['*']
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('CLOUDKITCHEN_DB_NAME'),
        'USER': os.getenv('CLOUDKITCHEN_DB_USER'),
        'PASSWORD': os.getenv('CLOUDKITCHEN_DB_PASSWORD'),
        'HOST': os.getenv('CLOUDKITCHEN_DB_HOST'),
        'PORT': os.getenv('CLOUDKITCHEN_DB_PORT'),
    }
}

