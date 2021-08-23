DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": "testdatabase"}}

DEBUG = True

INSTALLED_APPS = ["jsm_user_services"]

SECRET_KEY = "hewf!63(!t1j-9=8v%_tcg1_p1zz!5aywb%^b$vow17se!8y84"

USER_API_HOST = "http://ishtar-gate.dev.juntossomosmaisi.com.br/api/v1"
USER_API_TOKEN = "9f0350491d4355e3d4a966712d110d3e7d62a9c7"

JSM_USER_SERVICE_HTTP_TIMEOUT = 1e-6  # 0.000001

# DRF permissions
JSM_USER_SERVICES_DRF_APPEND_USER_DATA = True
JSM_USER_SERVICES_DRF_REQUEST_USER_DATA_ATTR_NAME = "user_data"
GOOGLE_RECAPTCHA_SECRET_KEY = "some_cool_secret"
