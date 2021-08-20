from django.urls import path

from lfl_admin.competitions.views import matches

urlpatterns = [

    path('Matches/Fetch/', matches.Matches_Fetch),
    path('Matches/Add', matches.Matches_Add),
    path('Matches/Update', matches.Matches_Update),
    path('Matches/Remove', matches.Matches_Remove),
    path('Matches/Lookup/', matches.Matches_Lookup),
    path('Matches/Info/', matches.Matches_Info),
    path('Matches/Copy', matches.Matches_Copy),

]
