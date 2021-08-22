from django.contrib import admin
from .models import ApiStatSpr

class ApiStatSprAdmin(admin.ModelAdmin):
    list_display = ('id', 'shortName', 'title', 'sql',)

admin.site.register(ApiStatSpr, ApiStatSprAdmin)