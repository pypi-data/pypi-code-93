from django.urls import path

from lfl_admin.statistic.views import raiting_of_players_division

urlpatterns = [

    path('Raiting_of_players_division/Fetch/', raiting_of_players_division.Raiting_of_players_division_Fetch),
    path('Raiting_of_players_division/Add', raiting_of_players_division.Raiting_of_players_division_Add),
    path('Raiting_of_players_division/Update', raiting_of_players_division.Raiting_of_players_division_Update),
    path('Raiting_of_players_division/Remove', raiting_of_players_division.Raiting_of_players_division_Remove),
    path('Raiting_of_players_division/Lookup/', raiting_of_players_division.Raiting_of_players_division_Lookup),
    path('Raiting_of_players_division/Info/', raiting_of_players_division.Raiting_of_players_division_Info),
    path('Raiting_of_players_division/Copy', raiting_of_players_division.Raiting_of_players_division_Copy),

]
