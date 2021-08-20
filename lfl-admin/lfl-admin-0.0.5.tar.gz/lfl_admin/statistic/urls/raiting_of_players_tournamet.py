from django.urls import path

from lfl_admin.statistic.views import raiting_of_players_tournamet

urlpatterns = [

    path('Raiting_of_players_tournamet/Fetch/', raiting_of_players_tournamet.Raiting_of_players_tournamet_Fetch),
    path('Raiting_of_players_tournamet/Add', raiting_of_players_tournamet.Raiting_of_players_tournamet_Add),
    path('Raiting_of_players_tournamet/Update', raiting_of_players_tournamet.Raiting_of_players_tournamet_Update),
    path('Raiting_of_players_tournamet/Remove', raiting_of_players_tournamet.Raiting_of_players_tournamet_Remove),
    path('Raiting_of_players_tournamet/Lookup/', raiting_of_players_tournamet.Raiting_of_players_tournamet_Lookup),
    path('Raiting_of_players_tournamet/Info/', raiting_of_players_tournamet.Raiting_of_players_tournamet_Info),
    path('Raiting_of_players_tournamet/Copy', raiting_of_players_tournamet.Raiting_of_players_tournamet_Copy),

]
