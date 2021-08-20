from django.urls import path

from lfl_admin.competitions.views import players_change_history_text_informations

urlpatterns = [

    path('Players_change_history_text_informations/Fetch/', players_change_history_text_informations.Players_change_history_text_informations_Fetch),
    path('Players_change_history_text_informations/Add', players_change_history_text_informations.Players_change_history_text_informations_Add),
    path('Players_change_history_text_informations/Update', players_change_history_text_informations.Players_change_history_text_informations_Update),
    path('Players_change_history_text_informations/Remove', players_change_history_text_informations.Players_change_history_text_informations_Remove),
    path('Players_change_history_text_informations/Lookup/', players_change_history_text_informations.Players_change_history_text_informations_Lookup),
    path('Players_change_history_text_informations/Info/', players_change_history_text_informations.Players_change_history_text_informations_Info),
    path('Players_change_history_text_informations/Copy', players_change_history_text_informations.Players_change_history_text_informations_Copy),

]
