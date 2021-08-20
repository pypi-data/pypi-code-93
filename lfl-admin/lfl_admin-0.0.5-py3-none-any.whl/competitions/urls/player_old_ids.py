from django.urls import path

from lfl_admin.competitions.views import player_old_ids

urlpatterns = [

    path('Player_old_ids/Fetch/', player_old_ids.Player_old_ids_Fetch),
    path('Player_old_ids/Add', player_old_ids.Player_old_ids_Add),
    path('Player_old_ids/Update', player_old_ids.Player_old_ids_Update),
    path('Player_old_ids/Remove', player_old_ids.Player_old_ids_Remove),
    path('Player_old_ids/Lookup/', player_old_ids.Player_old_ids_Lookup),
    path('Player_old_ids/Info/', player_old_ids.Player_old_ids_Info),
    path('Player_old_ids/Copy', player_old_ids.Player_old_ids_Copy),

]
