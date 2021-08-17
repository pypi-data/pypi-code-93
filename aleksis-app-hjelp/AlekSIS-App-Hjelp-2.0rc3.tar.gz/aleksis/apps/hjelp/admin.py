# noqa

from django.contrib import admin
from django.db.models import Model
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from .models import FAQQuestion, FAQSection, IssueCategory

MATERIAL_ICONS_CSS_URL = "/static/material-design-icons-iconfont/dist/material-design-icons.css"


class IconMixin(object):
    """Mixin for icon lookup."""

    def _icon(self, obj: Model) -> str:
        return format_html('<i class="material-icons">{}<i/>', obj.icon)


class FAQSectionAdmin(IconMixin, admin.ModelAdmin):
    """ModelAdmin for FAQ sections."""

    list_display = ("name", "_icon")

    class Media:
        css = {"all": (MATERIAL_ICONS_CSS_URL,)}


def show(modeladmin, request, queryset):
    queryset.update(show=True)


show.short_description = _("Publish selected questions")


def hide(modeladmin, request, queryset):
    queryset.update(show=False)


hide.short_description = _("Unpublish selected questions")


class FAQQuestionAdmin(IconMixin, admin.ModelAdmin):
    """ModelAdmin for FAQ questions."""

    list_display = ("question_text", "section", "_icon", "show")
    actions = [show, hide]

    class Media:
        css = {"all": (MATERIAL_ICONS_CSS_URL,)}


class IssueCategoryAdmin(IconMixin, admin.ModelAdmin):
    """ModelAdmin for issue categories."""

    list_display = ("name", "_icon", "parent", "placeholder", "free_text")

    class Media:
        css = {"all": (MATERIAL_ICONS_CSS_URL,)}


admin.site.register(FAQQuestion, FAQQuestionAdmin)
admin.site.register(FAQSection, FAQSectionAdmin)
admin.site.register(IssueCategory, IssueCategoryAdmin)
