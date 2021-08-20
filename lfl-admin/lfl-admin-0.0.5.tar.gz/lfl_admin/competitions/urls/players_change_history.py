from django.urls import path

from lfl_admin.competitions.views import players_change_history

urlpatterns = [

    path('Players_change_history/Fetch/', players_change_history.Players_change_history_Fetch),
    path('Players_change_history/Add', players_change_history.Players_change_history_Add),
    path('Players_change_history/Update', players_change_history.Players_change_history_Update),
    path('Players_change_history/Remove', players_change_history.Players_change_history_Remove),
    path('Players_change_history/Lookup/', players_change_history.Players_change_history_Lookup),
    path('Players_change_history/Info/', players_change_history.Players_change_history_Info),
    path('Players_change_history/Copy', players_change_history.Players_change_history_Copy),

]
