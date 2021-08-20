from django.urls import path

from lfl_admin.competitions.views import disqualifications

urlpatterns = [

    path('Disqualifications/Fetch/', disqualifications.Disqualifications_Fetch),
    path('Disqualifications/Add', disqualifications.Disqualifications_Add),
    path('Disqualifications/Update', disqualifications.Disqualifications_Update),
    path('Disqualifications/Remove', disqualifications.Disqualifications_Remove),
    path('Disqualifications/Lookup/', disqualifications.Disqualifications_Lookup),
    path('Disqualifications/Info/', disqualifications.Disqualifications_Info),
    path('Disqualifications/Copy', disqualifications.Disqualifications_Copy),

]
