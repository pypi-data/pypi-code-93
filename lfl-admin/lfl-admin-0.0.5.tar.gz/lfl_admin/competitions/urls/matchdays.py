from django.urls import path

from lfl_admin.competitions.views import matchdays

urlpatterns = [

    path('Matchdays/Fetch/', matchdays.Matchdays_Fetch),
    path('Matchdays/Add', matchdays.Matchdays_Add),
    path('Matchdays/Update', matchdays.Matchdays_Update),
    path('Matchdays/Remove', matchdays.Matchdays_Remove),
    path('Matchdays/Lookup/', matchdays.Matchdays_Lookup),
    path('Matchdays/Info/', matchdays.Matchdays_Info),
    path('Matchdays/Copy', matchdays.Matchdays_Copy),

]
