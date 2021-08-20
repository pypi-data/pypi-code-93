from django.urls import path

from lfl_admin.competitions.views import leagues_text_informations

urlpatterns = [

    path('Leagues_text_informations/Fetch/', leagues_text_informations.Leagues_text_informations_Fetch),
    path('Leagues_text_informations/Add', leagues_text_informations.Leagues_text_informations_Add),
    path('Leagues_text_informations/Update', leagues_text_informations.Leagues_text_informations_Update),
    path('Leagues_text_informations/Remove', leagues_text_informations.Leagues_text_informations_Remove),
    path('Leagues_text_informations/Lookup/', leagues_text_informations.Leagues_text_informations_Lookup),
    path('Leagues_text_informations/Info/', leagues_text_informations.Leagues_text_informations_Info),
    path('Leagues_text_informations/Copy', leagues_text_informations.Leagues_text_informations_Copy),

]
