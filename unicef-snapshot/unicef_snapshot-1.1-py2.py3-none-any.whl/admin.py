from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from unicef_snapshot.models import Activity
from unicef_snapshot.utils import create_dict_with_relations, create_snapshot


class SnapshotModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        pre_save = None
        if hasattr(obj, "pk") and obj.pk is not None:
            pre_save = obj.__class__.objects.get(pk=obj.pk)
        pre_save = create_dict_with_relations(pre_save)
        super().save_model(request, obj, form, change)
        create_snapshot(obj, pre_save, request.user)


class ActivityInline(GenericTabularInline):
    model = Activity
    ct_field = "target_content_type"
    ct_fk_field = "target_object_id"
    fields = ["action", "by_user_display", "change", "created"]
    readonly_fields = [
        "action",
        "by_user_display",
        "change",
        "created",
    ]
    extra = 0
    can_delete = False
    can_add = False

    def has_add_permission(self, request, obj=None):
        return False


class ActivityAdmin(admin.ModelAdmin):
    model = Activity
    readonly_fields = [
        'target_content_type',
        'target_object_id',
        'target',
        'action',
        'by_user_display',
        'data',
        'change',
        'created',
        'modified',
    ]
    list_display = (
        'target',
        'action',
        'by_user_display'
    )
    list_filter = (
        'action',
    )

    def has_add_permission(self, request):
        return False


admin.site.register(Activity, ActivityAdmin)
