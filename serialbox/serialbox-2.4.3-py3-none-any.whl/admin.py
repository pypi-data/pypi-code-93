from serialbox import models
from django.contrib import admin
from list_based_flavorpack.models import ListBasedRegion
from random_flavorpack.models import RandomizedRegion

class ResponseRuleAdmin(admin.ModelAdmin):
    list_display = ('pool', 'rule', 'content_type')
    search_fields = ('pool__readable_name','pool__machine_name')


class ResponseAdmin(admin.ModelAdmin):
    list_display = ('pool', 'type',
                    'size_granted', 'remote_host')
    search_fields = ('response',)


class RegionInline(admin.StackedInline):
    model = models.SequentialRegion
    extra = 0


class ListBasedInline(admin.StackedInline):
    model = ListBasedRegion
    extra = 0


class RandomRegionInline(admin.StackedInline):
    model = RandomizedRegion
    extra = 0


class PoolAdmin(admin.ModelAdmin):
    list_display = (
        'readable_name',
        'machine_name',
        'active'
    )
    search_fields = ['readable_name', 'machine_name']
    inlines = [RegionInline, ListBasedInline, RandomRegionInline]

def register_to_site(admin_site):
    admin_site.register(models.Pool, PoolAdmin)
    admin_site.register(models.ResponseRule, ResponseRuleAdmin)
    admin_site.register(models.Response, ResponseAdmin)

