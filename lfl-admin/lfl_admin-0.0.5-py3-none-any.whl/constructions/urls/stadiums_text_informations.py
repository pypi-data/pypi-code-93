from django.urls import path

from lfl_admin.constructions.views import stadiums_text_informations

urlpatterns = [

    path('Stadiums_text_informations/Fetch/', stadiums_text_informations.Stadiums_text_informations_Fetch),
    path('Stadiums_text_informations/Add', stadiums_text_informations.Stadiums_text_informations_Add),
    path('Stadiums_text_informations/Update', stadiums_text_informations.Stadiums_text_informations_Update),
    path('Stadiums_text_informations/Remove', stadiums_text_informations.Stadiums_text_informations_Remove),
    path('Stadiums_text_informations/Lookup/', stadiums_text_informations.Stadiums_text_informations_Lookup),
    path('Stadiums_text_informations/Info/', stadiums_text_informations.Stadiums_text_informations_Info),
    path('Stadiums_text_informations/Copy', stadiums_text_informations.Stadiums_text_informations_Copy),

]
