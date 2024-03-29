"""
Django settings for npe project.

Generated by 'django-admin startproject' using Django 4.2.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

import logging
from pathlib import Path
from dotenv import load_dotenv
import os
from django.contrib.messages import constants as messages
from django.utils.translation import gettext_lazy as _

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
CORE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app_name = "NoPucEsperar"
location_bias_for_google_maps = "rectangle:40.522,0.158|42.868,3.327"
'''
valor de latitud más arriba en cataluña = 42.868
valor de latitud más abajo en cataluña = 40.522
valor de longitud más a la izq en cataluña = 0.158
valor de longitud más a la der en cataluña = 3.327
definición de rectángulos para Google places = rectangle:south,west|north,east
'''
os.chdir(BASE_DIR)

# Logging init - Logger
logger = logging.getLogger(app_name)
logger.propagate = True
logger.setLevel(logging.DEBUG)
# Logging init - Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
# Logging init - Formatter
formatter = logging.Formatter('%(asctime)s [%(name)s] [%(levelname)s] %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
# Config loading
logger.info(f"Loading settings. Searching for .env...")


if Path(".env").is_file():
    logger.info("Environment file found. Loading settings from there.")
    load_dotenv()
else:
    logger.info("Environment file not found. Config is expected to come from environment variables.")
config_has_missing_params = False
missing_params = []
DEBUGMODE = DBHOST = DBPORT = DBUSER = DBPASSWORD = DBNAME = SECRET_KEY = ""
for configvalue in ["DEBUGMODE", "DBHOST", "DBPORT", "DBUSER", "DBPASSWORD", "DBNAME", "SECRET_KEY",
                    "NOMINATIM_API_KEY", "GOOGLE_API_KEY"]:
    if configvalue not in os.environ:
        missing_params.append(configvalue)
        config_has_missing_params = True
    else:
        valuetoset = os.getenv(configvalue)
        to_exec = f'{configvalue} = "{valuetoset}"'
        exec(to_exec)
if config_has_missing_params:
    logger.error(f"Missing mandatory parameters in config: {missing_params}")
    exit(1)

if DEBUGMODE.lower() in ("t", "1", "true"):  # if debug is disabled,
    DEBUG = True
    logger.info("Debug mode is ENABLED. Setting the logger to DEBUG level.")
    # Actually, loggers start in debug level, so we don't need to do anything
else:
    DEBUG = False
    logger.info("Debug mode is disabled. Setting the logger to INFO level.")
    # Lower down the verbosity of loggers, which we started in DEBUG level
    logger.setLevel(logging.INFO)
    console_handler.setLevel(logging.INFO)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Assets Management
ASSETS_ROOT = os.getenv('ASSETS_ROOT', '/static/assets')

ALLOWED_HOSTS = ['*']
# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'admin_api',
    'admin_interface',
    'authentication',
    'corsheaders',
    'crispy_forms',
    'crispy_bootstrap4'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CORS_ALLOWED_ORIGINS = [
    "https://admin.nopucesperar.org",
    "https://app.nopucesperar.org",
]

ROOT_URLCONF = 'core.urls'
LOGIN_REDIRECT_URL = "home"  # Route defined in home/urls.py
LOGOUT_REDIRECT_URL = "home"  # Route defined in home/urls.py
TEMPLATE_DIR = os.path.join(CORE_DIR, "admin_interface/templates")  # ROOT dir for templates

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.csrf',
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'admin_interface.context_processors.cfg_assets_root',
            ],
        },
    },
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

if DEBUG:
    logger.info('Using development database (SQLITE file).')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    logger.info('Using production database settings.')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': DBHOST,
            'PORT': DBPORT,
            'USER': DBUSER,
            'PASSWORD': DBPASSWORD,
            'NAME': DBNAME,
            'OPTIONS': {
                'charset': 'utf8mb4'
            }
        }
    }

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'ca'

LANGUAGES = [
    ('ca', _('Català')),
]

TIME_ZONE = 'Europe/Madrid'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# noinspection PyUnresolvedReferences
STATIC_ROOT = os.path.join(CORE_DIR, 'static')
STATIC_URL = '/static/'
# Extra places for collectstatic to find static files.
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'admin_interface/static'),
)

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

MESSAGE_TAGS = {
    messages.WARNING: "alert-warning",
    messages.ERROR: 'alert-danger',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success'
}
