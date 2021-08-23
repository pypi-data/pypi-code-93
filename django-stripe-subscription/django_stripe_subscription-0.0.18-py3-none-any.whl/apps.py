from configparser import ConfigParser
from pathlib import Path

from django.apps import AppConfig
from django.conf import settings
from django.core import mail


class StripeSubscriptionConfig(AppConfig):
    name = 'stripe_subscription'

    def ready(self):
        """
        Loads custom per domain SMTP configuration.
        SMTP config sample:
            stripe_subscription_smtp.ini

            [example.com]
            backend=django.core.mail.backends.smtp.EmailBackend
            host=smtp.example.com
            port=587
            username=someuser
            password=somepassword
            use_ssl=True

        Notification config sample:
            stripe_subscription_notificaions.ini

            [example.com]
            from_email=no-reply@example.com
            cancel_subscription_email_template=stripe_subscription/cancel-email.html
            cancel_subscription_success_template=stripe_subscription/cancel-success.html
        """

        # 1. Load SMTP settings
        smtp_config_path = settings.BASE_DIR / 'stripe_subscription_smtp.ini'

        if smtp_config_path.exists():
            self._smtp_config = ConfigParser()
            self._smtp_config.read(smtp_config_path)
        else:
            self._smtp_config = None

        # 2. Load notifications settings
        notification_config_path = settings.BASE_DIR / 'stripe_subscription_notificaions.ini'

        if notification_config_path.exists():
            self._notification_config = ConfigParser()
            self._notification_config.read(notification_config_path)
        else:
            self._notification_config = None

    def get_smtp_connection(self, host):
        """
        Returns SMTP connection for give host.
        Per host configuration store in settings.BASE_DIR / stripe_subscription_smtp.ini.
        If there is no configuration found for given host Django defaul STMP connection will be returned.

        :param host: Host name
        :returns: SMTP connection object
        """
        cfg = {}
        
        if self._smtp_config and host in self._smtp_config:
            cfg = dict(self._smtp_config[host])

        return mail.get_connection(**cfg)

    def get_from_email(self, host):
        """
        Returns notfications email for given host.
        If there is notification config for given host settings.DEFAULT_FROM_EMAIL
        will be returned.
        :return str:
        """
        cfg = {}
        
        if host in self._notification_config:
            cfg = dict(self._notification_config[host])

        return cfg.get('from_email', settings.DEFAULT_FROM_EMAIL)

    def get_template(self, host, category):
        """
        Returns notification email template for given host and category
        :param host: Host name
        :param category: Notification category (f.e. cancel-email, cancel-success)
        """
        cfg = {}
        
        if host in self._notification_config:
            cfg = dict(self._notification_config[host])

        return cfg.get(category, 'stripe_subscription/%s.html' % category)
