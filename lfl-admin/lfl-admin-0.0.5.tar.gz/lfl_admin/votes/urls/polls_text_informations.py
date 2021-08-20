from django.urls import path

from lfl_admin.votes.views import polls_text_informations

urlpatterns = [

    path('Polls_text_informations/Fetch/', polls_text_informations.Polls_text_informations_Fetch),
    path('Polls_text_informations/Add', polls_text_informations.Polls_text_informations_Add),
    path('Polls_text_informations/Update', polls_text_informations.Polls_text_informations_Update),
    path('Polls_text_informations/Remove', polls_text_informations.Polls_text_informations_Remove),
    path('Polls_text_informations/Lookup/', polls_text_informations.Polls_text_informations_Lookup),
    path('Polls_text_informations/Info/', polls_text_informations.Polls_text_informations_Info),
    path('Polls_text_informations/Copy', polls_text_informations.Polls_text_informations_Copy),

]
