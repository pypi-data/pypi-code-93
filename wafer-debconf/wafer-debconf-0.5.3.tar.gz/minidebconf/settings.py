from pathlib import Path
from django.conf import global_settings

from debconf.common_settings import *

INSTALLED_APPS = (
    'minidebconf',
    'debconf',
) + INSTALLED_APPS

WAFER_REGISTRATION_MODE = 'custom'
WAFER_USER_IS_REGISTERED = 'minidebconf.models.is_registered'

ROOT_URLCONF = 'minidebconf.urls'

basedir = Path(__file__).parent.absolute()

# manipulate middleware
MIDDLEWARE = list(MIDDLEWARE)

# i18n/l10n
session_idx = MIDDLEWARE.index("django.contrib.sessions.middleware.SessionMiddleware")
MIDDLEWARE.insert(session_idx, 'django.middleware.locale.LocaleMiddleware')
USE_I18N = True
USE_L10N = True
__languages__ = ['en'] + [p.name.replace('_', '-').lower()  for p in (basedir / 'locale').glob('*')]
LANGUAGES = [l for l in global_settings.LANGUAGES if l[0] in __languages__]
