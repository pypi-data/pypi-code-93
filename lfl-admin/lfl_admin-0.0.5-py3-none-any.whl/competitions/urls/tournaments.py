from django.urls import path

from lfl_admin.competitions.views import tournaments

urlpatterns = [

    path('Tournaments/Fetch/', tournaments.Tournaments_Fetch),
    path('Tournaments/Add', tournaments.Tournaments_Add),
    path('Tournaments/Update', tournaments.Tournaments_Update),
    path('Tournaments/Remove', tournaments.Tournaments_Remove),
    path('Tournaments/Lookup/', tournaments.Tournaments_Lookup),
    path('Tournaments/Info/', tournaments.Tournaments_Info),
    path('Tournaments/Copy', tournaments.Tournaments_Copy),
    path('Tournaments/Add_2_favorites', tournaments.Tournaments_Add_2_favorites),
    path('Tournaments/Del_from_favorites', tournaments.Tournaments_Del_from_favorites),

]
