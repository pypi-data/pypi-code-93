from django.urls import path

from lfl_admin.competitions.views import players

urlpatterns = [

    path('Players/Fetch/', players.Players_Fetch),
    path('Players/Add', players.Players_Add),
    path('Players/Update', players.Players_Update),
    path('Players/Remove', players.Players_Remove),
    path('Players/Lookup/', players.Players_Lookup),
    path('Players/Info/', players.Players_Info),
    path('Players/Copy', players.Players_Copy),

]
