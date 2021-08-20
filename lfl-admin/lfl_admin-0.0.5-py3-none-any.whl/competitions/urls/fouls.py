from django.urls import path

from lfl_admin.competitions.views import fouls

urlpatterns = [

    path('Fouls/Fetch/', fouls.Fouls_Fetch),
    path('Fouls/Add', fouls.Fouls_Add),
    path('Fouls/Update', fouls.Fouls_Update),
    path('Fouls/Remove', fouls.Fouls_Remove),
    path('Fouls/Lookup/', fouls.Fouls_Lookup),
    path('Fouls/Info/', fouls.Fouls_Info),
    path('Fouls/Copy', fouls.Fouls_Copy),

]
