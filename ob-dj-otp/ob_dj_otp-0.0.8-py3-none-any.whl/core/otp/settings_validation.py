import pkg_resources
from django.apps import apps
from django.conf import settings
from django.core.checks import Error

REQUIRED_INSTALLED_APPS = [
    "rest_framework",
]

REQUIRED_DEPENDENCIES = [
    "celery>=5",
]


def required_dependencies(app_configs, **kwargs):
    errors = []
    try:
        if getattr(settings, "OTP_PROVIDER", None):
            provider = getattr(settings, "OTP_PROVIDER")
            if provider == "twilio":
                REQUIRED_DEPENDENCIES.append("twilio>=6")
        pkg_resources.require(REQUIRED_DEPENDENCIES)
    except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict) as ex:
        errors.append(Error(ex.__str__()))
    return errors


def required_installed_apps(app_configs, **kwargs):
    errors = []
    for app in REQUIRED_INSTALLED_APPS:
        if not apps.is_installed(app):
            errors.append(Error(f"{app} is required in INSTALLED_APPS"))

    return errors


def required_settings(app_configs, **kwargs):
    errors = []
    if not getattr(settings, "OTP_PROVIDER", None):
        # TODO: Make options render from the wrapper options
        errors.append(
            Error(f"OTP_PROVIDER setting is required (available options: twilio/aws)")
        )
    if not getattr(settings, "OTP_TWILIO_SERVICE", None):
        errors.append(
            Error(
                f'OTP_TWILIO_SERVICE setting is required when setting "twilio" as OTP_PROVIDER'
            )
        )
    return errors
