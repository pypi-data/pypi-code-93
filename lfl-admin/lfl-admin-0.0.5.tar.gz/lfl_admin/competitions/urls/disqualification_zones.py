from django.urls import path

from lfl_admin.competitions.views import disqualification_zones

urlpatterns = [

    path('Disqualification_zones/Fetch/', disqualification_zones.Disqualification_zones_Fetch),
    path('Disqualification_zones/Add', disqualification_zones.Disqualification_zones_Add),
    path('Disqualification_zones/Update', disqualification_zones.Disqualification_zones_Update),
    path('Disqualification_zones/Remove', disqualification_zones.Disqualification_zones_Remove),
    path('Disqualification_zones/Lookup/', disqualification_zones.Disqualification_zones_Lookup),
    path('Disqualification_zones/Info/', disqualification_zones.Disqualification_zones_Info),
    path('Disqualification_zones/Copy', disqualification_zones.Disqualification_zones_Copy),

]
