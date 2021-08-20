from django.urls import path

from lfl_admin.competitions.views import referees

urlpatterns = [

    path('Referees/Fetch/', referees.Referees_Fetch),
    path('Referees/Add', referees.Referees_Add),
    path('Referees/Update', referees.Referees_Update),
    path('Referees/Remove', referees.Referees_Remove),
    path('Referees/Lookup/', referees.Referees_Lookup),
    path('Referees/Info/', referees.Referees_Info),
    path('Referees/Copy', referees.Referees_Copy),

]
