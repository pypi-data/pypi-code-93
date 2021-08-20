from django.urls import path

from lfl_admin.competitions.views import player_histories

urlpatterns = [

    path('Player_histories/Fetch/', player_histories.Player_histories_Fetch),
    path('Player_histories/Add', player_histories.Player_histories_Add),
    path('Player_histories/Update', player_histories.Player_histories_Update),
    path('Player_histories/Remove', player_histories.Player_histories_Remove),
    path('Player_histories/Lookup/', player_histories.Player_histories_Lookup),
    path('Player_histories/Info/', player_histories.Player_histories_Info),
    path('Player_histories/Copy', player_histories.Player_histories_Copy),

]
