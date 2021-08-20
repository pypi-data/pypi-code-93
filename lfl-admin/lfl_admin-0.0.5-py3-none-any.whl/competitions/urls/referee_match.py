from django.urls import path

from lfl_admin.competitions.views import referee_match

urlpatterns = [

    path('Referee_match/Fetch/', referee_match.Referee_match_Fetch),
    path('Referee_match/Add', referee_match.Referee_match_Add),
    path('Referee_match/Update', referee_match.Referee_match_Update),
    path('Referee_match/Remove', referee_match.Referee_match_Remove),
    path('Referee_match/Lookup/', referee_match.Referee_match_Lookup),
    path('Referee_match/Info/', referee_match.Referee_match_Info),
    path('Referee_match/Copy', referee_match.Referee_match_Copy),

]
