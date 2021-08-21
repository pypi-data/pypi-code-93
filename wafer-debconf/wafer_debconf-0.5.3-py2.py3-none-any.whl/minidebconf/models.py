from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from django_countries.fields import CountryField

from wafer.schedule.models import ScheduleBlock
from debconf.countries import Countries


INVOLVEMENT_LEVELS = (
    (0, _('Beginner')),
    (1, _('User')),
    (2, _('Contributor')),
    (4, _('Debian Maintainer (DM)')),
    (5, _('Debian Developer (DD)')),
)

GENDERS = (
    ('m', _('Male')),
    ('f', _('Female')),
    ('n', _('Non-Binary')),
)


class Registration(models.Model):
    class Meta:
        verbose_name = pgettext_lazy('conference', 'registration')
        verbose_name_plural = pgettext_lazy('conference', 'registrations')

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    # A minimal of personal information, for statistics
    involvement = models.IntegerField(
        null=True,
        blank=True,
        choices=INVOLVEMENT_LEVELS,
        verbose_name=_("Level of involvement with Debian"),
    )
    gender = models.CharField(
        max_length=1,
        blank=True,
        null=True,
        choices=GENDERS,
        verbose_name=_("Gender"),
    )
    country = CountryField(
        countries=Countries,
        null=True,
        blank=True,
        verbose_name=_("Country"),
    )
    city_state = models.CharField(
        max_length=128,
        blank=True,
        verbose_name=_("City/State or Province")
    )

    # attendance info
    days =  models.ManyToManyField(
        ScheduleBlock,
        verbose_name=_('Which days you will attend'),
    )

    @property
    def full_name(self):
        if self.user:
            return self.user.get_full_name()
        else:
            return None


def is_registered(user):
    return Registration.objects.filter(user=user).exists()
