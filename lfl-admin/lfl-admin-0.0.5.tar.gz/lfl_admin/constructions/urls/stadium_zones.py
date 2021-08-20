from django.urls import path

from lfl_admin.constructions.views import stadium_zones

urlpatterns = [

    path('Stadium_zones/Fetch/', stadium_zones.Stadium_zones_Fetch),
    path('Stadium_zones/Add', stadium_zones.Stadium_zones_Add),
    path('Stadium_zones/Update', stadium_zones.Stadium_zones_Update),
    path('Stadium_zones/Remove', stadium_zones.Stadium_zones_Remove),
    path('Stadium_zones/Lookup/', stadium_zones.Stadium_zones_Lookup),
    path('Stadium_zones/Info/', stadium_zones.Stadium_zones_Info),
    path('Stadium_zones/Copy', stadium_zones.Stadium_zones_Copy),

]
