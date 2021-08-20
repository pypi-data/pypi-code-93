from django.urls import path

from lfl_admin.competitions.views import squads

urlpatterns = [

    path('Squads/Fetch/', squads.Squads_Fetch),
    path('Squads/Add', squads.Squads_Add),
    path('Squads/Update', squads.Squads_Update),
    path('Squads/Remove', squads.Squads_Remove),
    path('Squads/Lookup/', squads.Squads_Lookup),
    path('Squads/Info/', squads.Squads_Info),
    path('Squads/Copy', squads.Squads_Copy),

]
