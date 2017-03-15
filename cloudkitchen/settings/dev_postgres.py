from cloudkitchen.settings.dev import *

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
