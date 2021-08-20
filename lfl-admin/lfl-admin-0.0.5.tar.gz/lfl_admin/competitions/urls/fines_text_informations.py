from django.urls import path

from lfl_admin.competitions.views import fines_text_informations

urlpatterns = [

    path('Fines_text_informations/Fetch/', fines_text_informations.Fines_text_informations_Fetch),
    path('Fines_text_informations/Add', fines_text_informations.Fines_text_informations_Add),
    path('Fines_text_informations/Update', fines_text_informations.Fines_text_informations_Update),
    path('Fines_text_informations/Remove', fines_text_informations.Fines_text_informations_Remove),
    path('Fines_text_informations/Lookup/', fines_text_informations.Fines_text_informations_Lookup),
    path('Fines_text_informations/Info/', fines_text_informations.Fines_text_informations_Info),
    path('Fines_text_informations/Copy', fines_text_informations.Fines_text_informations_Copy),

]
