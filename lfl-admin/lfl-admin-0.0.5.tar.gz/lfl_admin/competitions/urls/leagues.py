from django.urls import path

from lfl_admin.competitions.views import leagues

urlpatterns = [

    path('Leagues/Fetch/', leagues.Leagues_Fetch),
    path('Leagues/Add', leagues.Leagues_Add),
    path('Leagues/Update', leagues.Leagues_Update),
    path('Leagues/Remove', leagues.Leagues_Remove),
    path('Leagues/Lookup/', leagues.Leagues_Lookup),
    path('Leagues/Info/', leagues.Leagues_Info),
    path('Leagues/Copy', leagues.Leagues_Copy),

]
