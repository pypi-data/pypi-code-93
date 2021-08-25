from django.contrib import admin
from .models import Region, State, City, Address

# Register your models here.

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):

    list_display = [
        "name",
        "acronym",
    ]

    list_display_links = [
        "name",
        "acronym",
    ]
    
    search_fields = [
        "name",
        "acronym",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, *args):
        return False

    def has_delete_permission(self, request, *args):
        return False


@admin.register(State)
class StateAdmin(admin.ModelAdmin):

    list_display = [
        "name",
        "acronym",
        "region",
    ]

    list_display_links = [
        "name",
        "acronym",
        "region",
    ]

    list_filter = [
        "region",
    ]
    
    search_fields = [
        "name",
        "acronym",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, *args):
        return False

    def has_delete_permission(self, request, *args):
        return False


@admin.register(City)
class CityAdmin(admin.ModelAdmin):

    list_display = [
        "name",
        "state",
    ]

    list_display_links = [
        "name",
        "state",
    ]
    
    list_filter = [
        "state",
        "state__region",
    ]

    search_fields = [
        "name",
        "state__name",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, *args):
        return False

    def has_delete_permission(self, request, *args):
        return False


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):

    list_display = [
        "zipcode",
        "state",
        "city",
        "district",
        "address",
        "number",
    ]

    list_display_links = [
        "zipcode",
        "state",
        "city",
        "district",
        "address",
        "number",
    ]
    
    search_fields = [
        "zipcode",
        "state__name",
        "city__name",
        "district",
        "address",
        "number",
    ]

    autocomplete_fields = [
        "state",
        "city",
    ]
