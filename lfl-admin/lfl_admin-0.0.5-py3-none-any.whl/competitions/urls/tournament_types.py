from django.urls import path

from lfl_admin.competitions.views import tournament_types

urlpatterns = [

    path('Tournament_types/Fetch/', tournament_types.Tournament_types_Fetch),
    path('Tournament_types/Add', tournament_types.Tournament_types_Add),
    path('Tournament_types/Update', tournament_types.Tournament_types_Update),
    path('Tournament_types/Remove', tournament_types.Tournament_types_Remove),
    path('Tournament_types/Lookup/', tournament_types.Tournament_types_Lookup),
    path('Tournament_types/Info/', tournament_types.Tournament_types_Info),
    path('Tournament_types/Copy', tournament_types.Tournament_types_Copy),

]
