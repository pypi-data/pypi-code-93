from django.urls import path

from lfl_admin.region.views import region_zones

urlpatterns = [

    path('Region_zones/Fetch/', region_zones.Region_zones_Fetch),
    path('Region_zones/Add', region_zones.Region_zones_Add),
    path('Region_zones/Update', region_zones.Region_zones_Update),
    path('Region_zones/Remove', region_zones.Region_zones_Remove),
    path('Region_zones/Lookup/', region_zones.Region_zones_Lookup),
    path('Region_zones/Info/', region_zones.Region_zones_Info),
    path('Region_zones/Copy', region_zones.Region_zones_Copy),

]
