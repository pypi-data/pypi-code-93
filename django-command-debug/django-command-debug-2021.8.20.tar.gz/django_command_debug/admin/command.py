from django.contrib import admin

class CommandAdmin(admin.ModelAdmin):
    list_display = ['id','name','app','is_enabled']
    list_filter = ('app','is_enabled',)
    list_search = ('app','name',)
