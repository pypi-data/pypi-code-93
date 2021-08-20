from django.urls import path

from lfl_admin.competitions.views import squads_match

urlpatterns = [

    path('Squads_match/Fetch/', squads_match.Squads_match_Fetch),
    path('Squads_match/Add', squads_match.Squads_match_Add),
    path('Squads_match/Update', squads_match.Squads_match_Update),
    path('Squads_match/Remove', squads_match.Squads_match_Remove),
    path('Squads_match/Lookup/', squads_match.Squads_match_Lookup),
    path('Squads_match/Info/', squads_match.Squads_match_Info),
    path('Squads_match/Copy', squads_match.Squads_match_Copy),

]
