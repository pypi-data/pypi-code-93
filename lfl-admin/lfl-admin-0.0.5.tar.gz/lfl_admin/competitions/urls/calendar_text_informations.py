from django.urls import path

from lfl_admin.competitions.views import calendar_text_informations

urlpatterns = [

    path('Calendar_text_informations/Fetch/', calendar_text_informations.Calendar_text_informations_Fetch),
    path('Calendar_text_informations/Add', calendar_text_informations.Calendar_text_informations_Add),
    path('Calendar_text_informations/Update', calendar_text_informations.Calendar_text_informations_Update),
    path('Calendar_text_informations/Remove', calendar_text_informations.Calendar_text_informations_Remove),
    path('Calendar_text_informations/Lookup/', calendar_text_informations.Calendar_text_informations_Lookup),
    path('Calendar_text_informations/Info/', calendar_text_informations.Calendar_text_informations_Info),
    path('Calendar_text_informations/Copy', calendar_text_informations.Calendar_text_informations_Copy),

]
