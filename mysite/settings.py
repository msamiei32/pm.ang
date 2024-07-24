from pathlib import Path
import os
import django_heroku
from dotenv import load_dotenv

# load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-pzt1x3t)m-e@m@$*r&rpgvqpxjyl$r4^y7l8xl3iyfb2#4gf9^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
# USE_SQLITE = os.getenv('USE_SQLITE')

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # Third party apps
    'jalali_date',
    'crispy_forms',
    'ckeditor',
    'ckeditor_uploader',
    'widget_tweaks',
    # 'users.apps.UsersConfig'

    # apps
    'base.apps.BaseConfig',
    'users.apps.UsersConfig',
    'review.apps.ReviewConfig',
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

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'mysite.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
# DEFAULT_DATABASE_SQLITE = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': 'db.sqlite3',
#     }
# }



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR /'db.sqlite3',
        # 'NAME': 'pmangir1_ang',
        # 'USER': 'pmangir1_Amin09124139083',
        # 'PASSWORD': 'Amin@09124139083@',
        # 'HOST': '127.0.0.1',
        # 'PORT': '3306'
    }
}



# 'OPTION':{
#         'NAME':'pmangir1_ang',
#         'USER':'pmangir1_Amin09124139083',
#         'PASSWORD':'Amin@09124139083@',
#     }

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'fa-ir'

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CKEDITOR_BASEPATH = "/static/ckeditor/ckeditor/"
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'width': '100%',
    },
}

CRISPY_TEMPLATE_PACK = 'bootstrap4'

BOOTSTRAP4 = {
    'include_jquery': True,
}

# default settings
JALALI_DATE_DEFAULTS = {
    'Strftime': {
        'date': '%y/%m/%d',
        'datetime': '%H:%M:%S _ %y/%m/%d',
    },
    'Static': {
        'js': [
            # loading datepicker
            'admin/js/django_jalali.min.js',
            # OR
            # 'admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.core.js',
            # 'admin/jquery.ui.datepicker.jalali/scripts/calendar.js',
            # 'admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.datepicker-cc.js',
            # 'admin/jquery.ui.datepicker.jalali/scripts/jquery.ui.datepicker-cc-fa.js',
            # 'admin/js/main.js',
        ],
        'css': {
            'all': [
                'admin/jquery.ui.datepicker.jalali/themes/base/jquery-ui.min.css',
            ]
        }
    },
}

# CELERY_BEAT_SCHEDULE = {
#     "every_monday_morning": {
#         "task": "base.tasks.every_monday_morning",
#         "schedule": crontab(hour=2, minute=49),
#     },
# }
#
# CELERY_BROKER_URL = 'amqp://localhost'
# CELERY_RESULT_BACKEND = "amqp://localhost"
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ENABLE_UTC = False
# CELERY_TIMEZONE = "UTC"


LOGIN_URL = '/login/'

django_heroku.settings(locals())
