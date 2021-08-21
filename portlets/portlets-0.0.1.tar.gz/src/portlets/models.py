from django.conf import settings
from django.db import models
from django.db.models import Q
from django.db.models.fields.related_descriptors import ReverseOneToOneDescriptor
from django.template import Context, loader
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from model_utils.managers import InheritanceManager
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import (
    FieldPanel,
    InlinePanel,
    MultiFieldPanel,
    ObjectList,
    TabbedInterface,
)
from wagtail.core.models import Site


class Portlet(ClusterableModel):
    title = models.CharField(verbose_name=_('Title'), max_length=255)
    display_title = models.CharField(verbose_name=_('Display title'), max_length=255, blank=True)
    link = models.CharField(verbose_name=_('Link'), max_length=255, blank=True)
    portlet_type = models.SlugField(editable=False)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)

    objects = InheritanceManager()

    def slug(self):
        return slugify(self.title)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.portlet_type:
            self.portlet_type = self.__class__.__name__
        else:
            if self.portlet_type != self.__class__.__name__:
                self.portlet_type = self.__class__.__name__

        super(Portlet, self).save(*args, **kwargs)

    def update_type(self):
        self.portlet_type = self.__class__.__name__

    def get_frontend_display(self):
        subclass_verbose_name_plural = self.__class__.objects.get_subclass(
            pk=self.id,
        ).__class__._meta.verbose_name_plural

        if subclass_verbose_name_plural:
            return str(subclass_verbose_name_plural)

        return self.portlet_type

    def update(self, request):
        self.request = request

    def render(self):
        template = loader.get_template(self.__template__)
        context = Context({'portlet': self, 'request': self.request})
        return template.render(context)

    def vary_on(self):
        return [translation.get_language()]

    def get_object(self):
        return getattr(self, self.portlet_type.lower())

    def get_edit_link(self):
        # reverse admin url to get link to specific object
        return reverse(
            f'{self._meta.app_label}_{self.portlet_type.lower()}_modeladmin_edit', args=(self.pk,),
        )

    def is_assigned(self):
        return self.portletassignment_set.all().count() > 0

    @staticmethod
    def select_subclasses(*subclasses):
        if not subclasses:
            subclasses = Portlet.get_subclasses()
        new_qs = Portlet.objects.all().select_related(*subclasses)
        new_qs.subclasses = subclasses
        return new_qs

    @staticmethod
    def get_subclasses():
        return [
            field
            for field in dir(Portlet)
            if isinstance(getattr(Portlet, field), ReverseOneToOneDescriptor)
            and issubclass(getattr(Portlet, field).related.model, Portlet)
        ]

    assignment_panels = (
        MultiFieldPanel(
            [InlinePanel('related_assignments', heading='Related Assignments')],
            heading=_('Assignments'),
            classname='collapsible',
        ),
    )
    portlet_panels = [
        MultiFieldPanel([FieldPanel('title')], heading=_('Content'), classname='collapsible'),
    ]

    edit_handler = TabbedInterface(
        [
            ObjectList(portlet_panels, heading='Portlet'),
            ObjectList(assignment_panels, heading='Assignments'),
        ],
    )


def split_path(path):
    result = []
    listpath = path.strip('/').split('/')
    while len(listpath) > 0 and listpath != ['']:
        result.append(f"/{'/'.join(listpath)}/")
        listpath.pop()
    result.append('/')
    return result


class PortletAssignment(models.Model):
    portlet = ParentalKey(Portlet, on_delete=models.CASCADE, related_name='related_assignments')
    path = models.CharField(verbose_name=_('Path'), max_length=200, db_index=True)
    site = models.ForeignKey(Site, on_delete=models.SET_NULL, verbose_name=_('Сайт'), null=True)
    inherit = models.BooleanField(
        verbose_name=_('Inherit'),
        default=False,
        help_text=_('Inherits this portlet to all sub-paths'),
    )
    slot = models.CharField(verbose_name=_('Slot'), max_length=50, db_index=True)
    position = models.PositiveIntegerField(verbose_name=_('Position'), default=0)
    prohibit = models.BooleanField(
        verbose_name=_('Prohibit'), default=False, help_text=_('Blocks this portlet'),
    )
    language = models.CharField(
        verbose_name=_('Language'),
        max_length=5,
        db_index=True,
        blank=True,
        choices=settings.LANGUAGES,
        default='',
    )

    def __unicode__(self):
        return u'[%s] %s (%s) @ %s' % (self.portlet, self.slot, self.position, self.path)

    def save(self, *args, **kwargs):
        if self.pk is None and self.position == 0:
            self.position = PortletAssignment.objects.filter(path=self.path, slot=self.slot).count()
        super(PortletAssignment, self).save(*args, **kwargs)

    def move_up(self):
        return self.move(-1)

    def move_down(self):
        return self.move(1)

    def move(self, delta):
        # there is always just one portlet at one position, so if the position
        # we want is already taken, we swap
        desired_position = self.position + delta
        if desired_position < 0:
            desired_position = 0
        old_position = self.position
        conflict = False
        portlet_assigments = PortletAssignment.objects.filter(
            path=self.path, slot=self.slot, position=desired_position,
        )
        if portlet_assigments.count() > 0:
            conflict = True
            for portlet_assigment in portlet_assigments:
                portlet_assigment.position = 444
                portlet_assigment.save()
        self.position = desired_position
        self.save()
        if conflict:
            for portlet_assigment in portlet_assigments:
                portlet_assigment.position = old_position
                portlet_assigment.save()
        PortletAssignment.clean_order(self.path, self.slot)

    @staticmethod
    def clean_order(path=path, slot=slot):
        assignments = PortletAssignment.objects.filter(path=path, slot=slot).order_by(
            '-prohibit', 'position', '-path',
        )
        i = 0
        for assignment in assignments:
            assignment.position = i
            assignment.save()
            i += 1

    @staticmethod
    def move_path(old, new, keep_old=False):
        assignments = PortletAssignment.objects.filter(path__startswith=old)
        for assignment in assignments:
            assignment.path = assignment.path.replace(old, new)
            if keep_old:
                assignment.pk = None
            assignment.save()

    @staticmethod
    def get_for_path(path, slot, language, site):
        path = split_path(path)
        query = Q(path=path.pop(0))
        for p in path:
            # for other parts of path, check if there are inherited portlets
            query |= Q(path=p, inherit=True)
        return (
            PortletAssignment.objects.filter(query)
            .filter(slot=slot, site=site)
            .filter(Q(language=language) | Q(language=''))
            .select_related(*[f'portlet__{subclass}' for subclass in Portlet.get_subclasses()])
            .order_by('-prohibit', 'position', '-path')
        )

    class Meta:
        verbose_name = _('Portlet Assignment')
        verbose_name_plural = _('Portlet Assignments')
        ordering = ('position',)
        unique_together = ('portlet', 'path', 'slot', 'position', 'prohibit', 'language')