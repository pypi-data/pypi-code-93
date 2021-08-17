"""
Django settings for contentTree project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

PROJECT_PATH = os.path.realpath(os.path.dirname(__file__))

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '-(y#kx(+4mc7yg7opf=^d6w2s04b5@(1clrt(mnju0(f+26)(-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1',]

siteTemplates = os.path.realpath(os.path.join(PROJECT_PATH, '..', 'templates/'))        

TEMPLATE_DIRS = (
    '/var/osmt/djangoRegistration/django-rotldrt-master/registration_bootstrap_3/templates/',
    #'../registration_bootstrap_3/templates/',
    siteTemplates,
    '../registration_bootstrap_3/templates/',
    '/usr/local/lib/python2.7/dist-packages/runcommands/templates/',    
)

TEMPLATE_LOADERS = (
     'django.template.loaders.filesystem.Loader',
     'django.template.loaders.app_directories.Loader',
     'apptemplates.Loader',
)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'registration',
    'bootstrap3',
    'django_logtail',
    'contentTree',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'contentTree.urls'

WSGI_APPLICATION = 'contentTree.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Australia/Melbourne'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
# STATICFILES_DIRS = (
#     os.path.join(BASE_DIR, "static"),
# )

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.realpath(os.path.join(PROJECT_PATH, '..', 'static'))
#STATIC_ROOT = "/acct/subs/banan/1/mohsen/lcaDjango/demo/static"


LOGTAIL_FILES = {
    'example': '/acct/subs/banan/1/mohsen/lcaDjango/demo/manage.py',
    'other': '/acct/subs/banan/1/mohsen/lcaDjango/demo/myManage.py',    
    'apacheAccess': '/var/log/apache2/access.log',
    'apacheError': '/var/log/apache2/error.log',    
}

LOGTAIL_UPDATE_INTERVAL = 50000 # Default is 3000 (three second)    
    
#
# Output emails to console for demo purposes.
#
#EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_ENABLE = 1

EMAIL_HOST='mail.t-mobile.com'
EMAIL_PORT = '25'
#EMAIL_USE_TLS='True'



ACCOUNT_ACTIVATION_DAYS = 3
LOGIN_REDIRECT_URL = '/'

#ADMIN_MEDIA_PREFIX = '/admin_media/'
