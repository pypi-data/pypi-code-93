from django.contrib import admin
from django.utils.timesince import timesince

class MessageAdmin(admin.ModelAdmin):
    list_display = ['id','app','name','pid','msg','created_at','created_at_timesince']
    list_filter = ('app','name',)
    list_search = ('msg',)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def created_at_timesince(self, debug):
        return timesince(debug.created_at).split(',')[0]+' ago' if debug.created_at else None
    created_at_timesince.short_description = ''
