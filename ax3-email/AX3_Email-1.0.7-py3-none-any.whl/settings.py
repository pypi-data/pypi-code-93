from django.conf import settings


EMAIL_BACKEND = getattr(
    settings,
    'AX3_EMAIL_BACKEND',
    'django.core.mail.backends.smtp.EmailBackend'
)
RETRIES = getattr(settings, 'AX3_RETRIES', 3)
DELAY = getattr(settings, 'AX3_DELAY', 600)
