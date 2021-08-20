from django.urls import path

from lfl_admin.competitions.views import referee_zone

urlpatterns = [

    path('Referee_zone/Fetch/', referee_zone.Referee_zone_Fetch),
    path('Referee_zone/Add', referee_zone.Referee_zone_Add),
    path('Referee_zone/Update', referee_zone.Referee_zone_Update),
    path('Referee_zone/Remove', referee_zone.Referee_zone_Remove),
    path('Referee_zone/Lookup/', referee_zone.Referee_zone_Lookup),
    path('Referee_zone/Info/', referee_zone.Referee_zone_Info),
    path('Referee_zone/Copy', referee_zone.Referee_zone_Copy),

]
