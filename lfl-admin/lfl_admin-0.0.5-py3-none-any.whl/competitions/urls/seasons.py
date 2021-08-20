from django.urls import path

from lfl_admin.competitions.views import seasons

urlpatterns = [

    path('Seasons/Fetch/', seasons.Seasons_Fetch),
    path('Seasons/Add', seasons.Seasons_Add),
    path('Seasons/Update', seasons.Seasons_Update),
    path('Seasons/Remove', seasons.Seasons_Remove),
    path('Seasons/Lookup/', seasons.Seasons_Lookup),
    path('Seasons/Info/', seasons.Seasons_Info),
    path('Seasons/Copy', seasons.Seasons_Copy),

]
