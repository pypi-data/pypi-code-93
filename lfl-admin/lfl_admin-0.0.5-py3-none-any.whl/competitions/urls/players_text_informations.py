from django.urls import path

from lfl_admin.competitions.views import players_text_informations

urlpatterns = [

    path('Players_text_informations/Fetch/', players_text_informations.Players_text_informations_Fetch),
    path('Players_text_informations/Add', players_text_informations.Players_text_informations_Add),
    path('Players_text_informations/Update', players_text_informations.Players_text_informations_Update),
    path('Players_text_informations/Remove', players_text_informations.Players_text_informations_Remove),
    path('Players_text_informations/Lookup/', players_text_informations.Players_text_informations_Lookup),
    path('Players_text_informations/Info/', players_text_informations.Players_text_informations_Info),
    path('Players_text_informations/Copy', players_text_informations.Players_text_informations_Copy),

]
