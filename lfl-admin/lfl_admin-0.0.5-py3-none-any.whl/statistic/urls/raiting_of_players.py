from django.urls import path

from lfl_admin.statistic.views import raiting_of_players

urlpatterns = [

    path('Raiting_of_players/Fetch/', raiting_of_players.Raiting_of_players_Fetch),
    path('Raiting_of_players/Add', raiting_of_players.Raiting_of_players_Add),
    path('Raiting_of_players/Update', raiting_of_players.Raiting_of_players_Update),
    path('Raiting_of_players/Remove', raiting_of_players.Raiting_of_players_Remove),
    path('Raiting_of_players/CalcStatic', raiting_of_players.Raiting_of_players_CalcStatic),
    path('Raiting_of_players/Lookup/', raiting_of_players.Raiting_of_players_Lookup),
    path('Raiting_of_players/Info/', raiting_of_players.Raiting_of_players_Info),
    path('Raiting_of_players/Copy', raiting_of_players.Raiting_of_players_Copy),

]
