from diplomv.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'attendance',
        'USER': 'postgres',
        'PASSWORD': 'the_most_secret_password_in_the_world',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}