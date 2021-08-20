from django.urls import path

from lfl_admin.competitions.views import disqualifications_text_informations

urlpatterns = [

    path('Disqualifications_text_informations/Fetch/', disqualifications_text_informations.Disqualifications_text_informations_Fetch),
    path('Disqualifications_text_informations/Add', disqualifications_text_informations.Disqualifications_text_informations_Add),
    path('Disqualifications_text_informations/Update', disqualifications_text_informations.Disqualifications_text_informations_Update),
    path('Disqualifications_text_informations/Remove', disqualifications_text_informations.Disqualifications_text_informations_Remove),
    path('Disqualifications_text_informations/Lookup/', disqualifications_text_informations.Disqualifications_text_informations_Lookup),
    path('Disqualifications_text_informations/Info/', disqualifications_text_informations.Disqualifications_text_informations_Info),
    path('Disqualifications_text_informations/Copy', disqualifications_text_informations.Disqualifications_text_informations_Copy),

]
