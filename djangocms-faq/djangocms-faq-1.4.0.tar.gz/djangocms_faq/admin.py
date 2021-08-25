from cms.admin.placeholderadmin import PlaceholderAdminMixin
from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from .models import FaqPluginModel, Keyword, QuestionFaqPluginModel


class DjangocmsFaqFaqPluginModel(PlaceholderAdminMixin, admin.ModelAdmin):
    list_display = ("name", "language", "get_page_url", "id")

    def get_queryset(self, request):
        qs = (
            super(DjangocmsFaqFaqPluginModel, self)
            .get_queryset(request)
            .exclude(placeholder__page__publisher_is_draft=False)
        )
        return qs

    def render_change_form(self, request, context, *args, **kwargs):
        self.change_form_template = "admin/change_form_help_text.html"
        extra = {
            "help_text": mark_safe(
                _(
                    "<i>Editing the faq using the django admin will only update the draft page, you will need to refresh the page to see the changes, and publish the page to made the changes appear on the live page.</i>"
                )
            )
        }
        context.update(extra)
        return super(DjangocmsFaqFaqPluginModel, self).render_change_form(
            request, context, *args, **kwargs
        )


class DjangocmsFaqQuestionFaqPluginModel(PlaceholderAdminMixin, admin.ModelAdmin):
    list_display = ("question", "language", "get_page_url", "id")
    autocomplete_fields = ("keywords",)

    def get_queryset(self, request):
        qs = (
            super(DjangocmsFaqQuestionFaqPluginModel, self)
            .get_queryset(request)
            .exclude(placeholder__page__publisher_is_draft=False)
        )
        return qs

    def render_change_form(self, request, context, *args, **kwargs):
        self.change_form_template = "admin/change_form_help_text.html"
        extra = {
            "help_text": mark_safe(
                _(
                    "<i>Editing a question using the django admin will only update the draft version, you will need to refresh the page to see the changes, and publish the page to made the changes appear on the live page.</i>"
                )
            )
        }
        context.update(extra)
        return super(DjangocmsFaqQuestionFaqPluginModel, self).render_change_form(
            request, context, *args, **kwargs
        )


class DjangocmsFaqKeywordAdmin(admin.ModelAdmin):

    list_display = ("id", "keyword")
    fieldsets = (("Add a keyword", {"fields": ("keyword",)}),)

    search_fields = ["question_text"]


admin.site.register(Keyword, DjangocmsFaqKeywordAdmin)
admin.site.register(QuestionFaqPluginModel, DjangocmsFaqQuestionFaqPluginModel)
admin.site.register(FaqPluginModel, DjangocmsFaqFaqPluginModel)
