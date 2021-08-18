'''
    Copyright 2018 SerialLab, CORP

    This file is part of SerialBox.

    SerialBox is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    SerialBox is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with SerialBox.  If not, see <http://www.gnu.org/licenses/>.
'''
import re

from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

from serialbox import errors
from django.core.exceptions import ValidationError
from django.db.models.signals import pre_save

# https://regex101.com/r/ZFOtT8/1
machine_name_regex = r'^[A-Za-z0-9\-\_]*$'
machine_name_validator = RegexValidator(
    machine_name_regex,
    _('Only numbers and letters are allowed. '
      'Invalid API Key.'))


class BaseModel(models.Model):
    created_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created Date'),
        help_text=_('The date and time that '
                    'this record was created'),
        db_index=True)
    modified_date = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Last Modified'),
        help_text=_(
            'The date and time that this'
            ' record was modified last.'),
        db_index=True)

    class Meta:
        abstract = True


class Pool(BaseModel):
    '''
    The base class for a simple number pool. A number pool consists of one or
    more regions.
    '''
    readable_name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name=_('Readable Name'),
        help_text=_(
            'A human-readable name for use in GUIs and '
            'reports and such.'),
        unique=True)
    machine_name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name=_('API Key'),
        help_text=_(
            'A url/api-friendly unique key for use in API calls and '
            'such.'),
        validators=[
            machine_name_validator,
        ],
        unique=True)
    active = models.BooleanField(
        default=True,
        verbose_name=_('Active'),
        help_text=_(
            'Whether or not this pool is active/in-use. '
            'If marked false the pool will no longer be '
            'able to be used in API calls, etc.'))

    request_threshold = models.BigIntegerField(
        default=50000,
        verbose_name=_('Threshold'),
        help_text=_(
            'The maximimum number of items that can be '
            'requested from this pool at once.  Default of '
            '50000.'))

    def __str__(self):
        return self.readable_name

    class Meta:
        verbose_name = _('Pool')
        verbose_name_plural = _('Pools')
        permissions = (
            ('allocate_numbers', 'Can allocate numbers.'),
        )
        ordering = [
            'readable_name',
            'machine_name'
        ]


CONTENT_TYPE_CHOICES = (
    ('xml', 'xml'),
    ('json', 'json'),
    ('yaml', 'yaml'),
    ('csv', 'csv')
)


class ResponseRule(BaseModel):
    """
    The response rule is used as part of post processing of number requests
    if the ResponseRule post processing rule is enabled.
    """
    content_type = models.CharField(
        max_length=100,
        verbose_name=_("Content Type"),
        help_text=_("The content type this response rule will handle."),
        null=True,
        choices=CONTENT_TYPE_CHOICES
    )
    pool = models.ForeignKey(
        'serialbox.Pool',
        on_delete=models.SET_NULL,
        null=True,
        help_text=_('The Pool to associate this response configuration with.'),
        verbose_name=_('Pool')
    )
    rule = models.ForeignKey(
        'quartet_capture.Rule',
        on_delete=models.SET_NULL,
        null=True,
        help_text=_('The rule to execute during response generation.')
    )

    class Meta:
        unique_together = ('content_type', 'pool')


class Region(BaseModel):
    '''
    One or more regions are defined within a given pool.
    '''
    readable_name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name=_('Readable Name'),
        help_text=_(
            'A human-readable name for use in GUIs and '
            'reports and such.'),
        unique=True)
    machine_name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name=_('API Key'),
        help_text=_(
            'A url/api-friendly unique key for use in API calls and '
            'such.'),
        validators=[
            machine_name_validator,
        ],
        unique=True)
    active = models.BooleanField(
        default=True,
        verbose_name=_('Active'),
        help_text=_(
            'Whether or not this pool is active/in-use. '
            'If marked false the pool will no longer be '
            'able to be used in API calls, etc.'))
    order = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_('Order'),
        help_text=_(
            'The order in which this region will be '
            'consumed as numbers are issued from the pool '
            'overall'))
    pool = models.ForeignKey(
        Pool,
        null=True,
        blank=True,
        verbose_name=_('Number Pool'),
        help_text=_('The Number Pool this region will '
                    'belong to.'),
        on_delete=models.CASCADE)

    def __str__(self):
        '''
        Return the human readable name for any interface elements.
        '''
        return self.readable_name

    class Meta(object):
        abstract = True
        unique_together = ('pool', 'order')


class SequentialRegion(Region):
    '''
    A SequentialRegion represents a pool of numbers that contain a start and
    end value as opposed to a list or random pool of numbers which have
    different properties to express their bounds.
    '''

    @staticmethod
    def pre_save(sender, instance, **kwargs):
        '''
        If there is no state set, default to the start.
        '''
        if instance.state is None:
            instance.state = instance.start

    start = models.BigIntegerField(null=False, blank=False, verbose_name=_(
        'Starting Number'), help_text=_(
        'The starting number for this region.'))
    end = models.BigIntegerField(null=False, blank=False, verbose_name=_(
        'Ending Number'), help_text=_('The ending number for this region.'))
    state = models.BigIntegerField(null=False, blank=False, verbose_name=_(
        'State'), help_text=_('The State represents the current number in use '
                              'if an API request were to come in now.'))

    def save(self, *args, **kwargs):
        '''
        Sets the state equal to the start if no start was supplied.  Also
        enforce a remaining property/attribute.
        '''
        if not self.state:
            self.state = self.start
        if not self.order:
            self._establish_order()
        if not hasattr(self, 'remaining'):
            # TODO: maybe put this check somewhere else?
            raise AttributeError(_('Region instances must have a remaining '
                                   'attribute that indicates how many numbers '
                                   'are left in the Region.'))
        from serialbox.utils import check_sequential_region_boundaries
        check_sequential_region_boundaries(self)
        super(SequentialRegion, self).save(*args, **kwargs)

    def _establish_order(self):
        '''
        Establish order where there is none. :-)
        '''
        regions = SequentialRegion.objects.filter(pool=self.pool).aggregate(
            models.Max('order')
        )
        val = regions['order__max'] or 0 + 1
        self.order = val + 1

    def __str__(self):
        '''
        Return the human readable name for any interface elements.
        '''
        return self.readable_name

    @property
    def remaining(self):
        '''
        Returns the number of numbers remaining in the current SequentialRegion
        '''
        return self.end - (self.state - 1)

    def clean(self):
        try:
            from serialbox.utils import check_sequential_region_boundaries
            check_sequential_region_boundaries(self)
        except errors.RegionBoundaryException as e:
            raise ValidationError(_(e.detail))

    def clean_fields(self, exclude=None):
        if not self.state:
            self.state = self.start
        Region.clean_fields(self, exclude=exclude)

    class Meta(object):
        verbose_name = _('Sequential Region')
        verbose_name_plural = _('Sequential Regions')


class ResponseTemplate(BaseModel):
    '''
    The configuration of a Jinja2 template to use when responding to API
    requests for number pool data.
    '''
    readable_name = models.CharField(max_length=100, null=False, blank=False,
                                     verbose_name=_('Name'), help_text=_(
            'The name of the template.'))
    description = models.TextField(verbose_name=_('Description'), help_text=_(
        'A brief description of what this template does.'))
    template_text = models.TextField(
        null=False,
        blank=False,
        verbose_name=_('Template Text'),
        help_text=_(
            'The template text using '
            'Jinja2 format markup.  For more info on Jinja templates '
            'see http://jinja.pocoo.org/'))
    pool = models.ManyToManyField(
        Pool, verbose_name=_('Pools'), help_text=_(
            'This will associate a response '
            'template with a pool.  If there is only one associated '
            'then it will be the default.  If there is more than one '
            'then the template must be explicitly defined on any API '
            'requests.'))

    def __str__(self):
        return self.readable_name

    class Meta(object):
        verbose_name = _('Response Template')
        verbose_name_plural = _('Response Templates')


class Response(BaseModel):
    '''
    Stores each response that the system has made.
    '''
    TYPE_CHOICES = (
        ('sequential', 'Sequential'),
        ('random', 'Random'),
        ('list', 'List'),
    )
    ENCODING_CHOICES = (
        ('base-36', 'Base 36 (1-9, A-Z)'),
        ('hex', 'Base 16 (0-F)'),
        ('decimal', 'Base 10 (0-9)')
    )
    fulfilled = models.BooleanField(
        verbose_name=_('Fulfilled'),
        help_text=_(
            'Whether or not the full request was fulfilled '
            'by the system'),
        null=False,
        blank=False)
    type = models.CharField(
        null=False,
        blank=False,
        max_length=10,
        verbose_name=_('Type'),
        help_text=_(
            'The type of response- either sequential, random, or '
            'list based.'),
        choices=TYPE_CHOICES)
    encoding = models.CharField(
        max_length=10,
        verbose_name=_('Encoding'),
        help_text=_(
            'The number encoding, choices are base-36, hex or '
            'decimal.'),
        choices=ENCODING_CHOICES,
        default='decimal')
    pool = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name=_('Pool'),
        help_text=_(
            'The machine_name value of the Pool that served '
            'the request.'))
    region = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name=_('Region'),
        help_text=_(
            'The machine_name of the Region that served the '
            'request.  This may be any type of region.'))
    size_granted = models.IntegerField(
        verbose_name=_('Size Granted'),
        help_text=_(
            'The number of serial numbers that were actually '
            'granted from the given pool.'))
    remote_host = models.CharField(
        max_length=400,
        verbose_name=_('Remote Host'),
        help_text=_('The remote host which made the request.'))
    task_name = models.CharField(
        max_length=100,
        verbose_name=_('Task Name'),
        help_text=_('If a response rule was configured for the pool '
                    'and the request was fulfilled, a task name '
                    'will be supplied.'))
    response = models.TextField(
        verbose_name=_("Response"),
        help_text=_("The response data"),
        null=True,
        blank=True
    )

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if hasattr(self, "number_list"):
            self.response = self.number_list
        super().save(force_insert, force_update, using, update_fields)

    def get_number_list(self):
        return self.number_list

    class Meta(object):
        verbose_name = _('Request and Response')
        verbose_name_plural = _('Requests and Responses')

    def __str__(self):
        return '{0}'.format(self.created_date)


pre_save.connect(SequentialRegion.pre_save, SequentialRegion)
