from django.urls import path

from lfl_admin.competitions.views import player_tournament_cards_limit

urlpatterns = [

    path('Player_tournament_cards_limit/Fetch/', player_tournament_cards_limit.Player_tournament_cards_limit_Fetch),
    path('Player_tournament_cards_limit/Add', player_tournament_cards_limit.Player_tournament_cards_limit_Add),
    path('Player_tournament_cards_limit/Update', player_tournament_cards_limit.Player_tournament_cards_limit_Update),
    path('Player_tournament_cards_limit/Remove', player_tournament_cards_limit.Player_tournament_cards_limit_Remove),
    path('Player_tournament_cards_limit/Lookup/', player_tournament_cards_limit.Player_tournament_cards_limit_Lookup),
    path('Player_tournament_cards_limit/Info/', player_tournament_cards_limit.Player_tournament_cards_limit_Info),
    path('Player_tournament_cards_limit/Copy', player_tournament_cards_limit.Player_tournament_cards_limit_Copy),

]
