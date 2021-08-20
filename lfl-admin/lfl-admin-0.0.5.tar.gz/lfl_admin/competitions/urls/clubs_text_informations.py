from django.urls import path

from lfl_admin.competitions.views import clubs_text_informations

urlpatterns = [

    path('Clubs_text_informations/Fetch/', clubs_text_informations.Clubs_text_informations_Fetch),
    path('Clubs_text_informations/Add', clubs_text_informations.Clubs_text_informations_Add),
    path('Clubs_text_informations/Update', clubs_text_informations.Clubs_text_informations_Update),
    path('Clubs_text_informations/Remove', clubs_text_informations.Clubs_text_informations_Remove),
    path('Clubs_text_informations/Lookup/', clubs_text_informations.Clubs_text_informations_Lookup),
    path('Clubs_text_informations/Info/', clubs_text_informations.Clubs_text_informations_Info),
    path('Clubs_text_informations/Copy', clubs_text_informations.Clubs_text_informations_Copy),

]
