from django.urls import path

from lfl_admin.region.views import regions

urlpatterns = [

    path('Regions/Fetch/', regions.Regions_Fetch),
    path('Regions/Add', regions.Regions_Add),
    path('Regions/Update', regions.Regions_Update),
    path('Regions/Remove', regions.Regions_Remove),
    path('Regions/Lookup/', regions.Regions_Lookup),
    path('Regions/Info/', regions.Regions_Info),
    path('Regions/Copy', regions.Regions_Copy),

]
