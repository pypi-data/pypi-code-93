import uuid

from cms.models.pluginmodel import CMSPlugin
from django import template
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import activate, deactivate, ugettext as _


register = template.Library()

# todo: virer display title
# laisser nom (privé) + page dans liste
# rendre nom obligatoire


class FaqPluginModel(CMSPlugin):
    title = models.CharField(
        _("Title"),
        max_length=300,
        blank=True,
        help_text=_(
            "Optional. Title that will be displayed on top of the FAQ. If not specified, nothing will be displayed."
        ),
    )
    name = models.CharField(
        _("Name"),
        max_length=300,
        default="No name",
        help_text=_(
            "Required. Will not be displayed on the website. Used to distinguish between several faqs.<br />"
        ),
    )
    uuid = models.UUIDField(primary_key=False, editable=False, default=uuid.uuid4)

    def get_page_url(self):
        try:
            activate(self.language)
            # thx https://stackoverflow.com/a/47953774/6813732
            url = mark_safe(
                '<a href="'
                + self.placeholder.page.get_absolute_url()
                + '" target="_blank">'
                + self.placeholder.page.get_page_title()
                + "</a>"
            )
            deactivate()
            return url
        except AttributeError:
            return _("Not on a page (maybe an apphook, like the blog)")

    get_page_url.short_description = _("Page")

    class Meta:
        verbose_name = _("Faq Container")

    def __unicode__(self):
        try:
            return f"{self.name} ({self.placeholder.page})"
        except AttributeError:
            return f"{self.name} ({self.placeholder.page}) − " + _("Draft")

    def __str__(self):
        try:
            return f"{self.name} ({self.placeholder.page})"
        except AttributeError:
            return f"{self.name} ({self.placeholder.page}) - " + _("Draft")

    def copy_relations(self, oldinstance):
        for relation in RelationSearchFaq.objects.filter(faq=self.uuid):
            faq = SearchFaqPluginModel.objects.filter(uuid=relation.faq)
            faq.search_in.add(self)


class QuestionFaqPluginModel(CMSPlugin):
    question = models.CharField(_("Question"), max_length=300)
    keywords = models.ManyToManyField(
        "djangocms_faq.keyword", verbose_name=_("Keywords")
    )
    slug = models.SlugField(
        blank=True,
        default="",
        help_text=_(
            "Unique slug for this question. Keep empty to let it be auto-generated. <br /><i>Warning: There is no control that the slug is unique, so you have to update it yourself if there is another question on the same page with the same slug.</i>"
        ),
        max_length=300,
    )

    @property
    def get_full_url(self):
        try:
            return self.placeholder.page.get_absolute_url()
        except AttributeError:
            return ""

    def get_page_url(self):
        try:
            activate(self.language)
            # thx https://stackoverflow.com/a/47953774/6813732
            url = mark_safe(
                '<a href="'
                + self.placeholder.page.get_absolute_url()
                + '" target="_blank">'
                + self.placeholder.page.get_page_title()
                + "</a>"
            )
            deactivate()
            return url
        except AttributeError:
            return _("Not on a page (maybe an apphook, like the blog)")

    get_page_url.short_description = _("Page")

    def copy_relations(self, oldinstance):
        self.keywords.set(oldinstance.keywords.all())

    class Meta:
        verbose_name = _("Faq Question")

    def __unicode__(self):
        return f"Faq Question − {self.question}"

    def save(self, **kwargs):
        if self.slug == "":
            self.slug = slugify(self.question)
        super().save(**kwargs)


class Keyword(models.Model):
    keyword = models.CharField(_("Keyword"), max_length=100)

    def __unicode__(self):
        return f"{self.keyword}"

    def __str__(self):
        return f"{self.keyword}"


class SearchFaqPluginModel(CMSPlugin):
    name = models.CharField(_("Search name"), max_length=50)
    search_in = models.ManyToManyField(
        "djangocms_faq.faqpluginmodel",
        verbose_name=_("Search in"),
        limit_choices_to={"placeholder__page__publisher_is_draft": True},
        help_text=_("Format: name (source page name).<br />"),
    )
    uuid = models.UUIDField(primary_key=False, editable=False, default=uuid.uuid4)

    class Meta:
        verbose_name = _("Faq Search")

    def __unicode__(self):
        return f"Faq Search − {self.name}"

    def copy_relations(self, oldinstance):
        self.search_in.set(oldinstance.search_in.all())

        for faq in self.search_in.all():
            if not RelationSearchFaq.objects.filter(search=self.uuid, faq=faq.uuid):
                new_relation = RelationSearchFaq()
                new_relation.faq = self.uuid
                new_relation.search = faq.uuid
                new_relation.save()


class RelationSearchFaq(models.Model):
    faq = models.UUIDField(editable=False)
    search = models.UUIDField(editable=False)
