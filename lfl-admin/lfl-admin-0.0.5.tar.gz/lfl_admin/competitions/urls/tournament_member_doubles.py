from django.urls import path

from lfl_admin.competitions.views import tournament_member_doubles

urlpatterns = [

    path('Tournament_member_doubles/Fetch/', tournament_member_doubles.Tournament_member_doubles_Fetch),
    path('Tournament_member_doubles/Add', tournament_member_doubles.Tournament_member_doubles_Add),
    path('Tournament_member_doubles/Update', tournament_member_doubles.Tournament_member_doubles_Update),
    path('Tournament_member_doubles/Remove', tournament_member_doubles.Tournament_member_doubles_Remove),
    path('Tournament_member_doubles/Lookup/', tournament_member_doubles.Tournament_member_doubles_Lookup),
    path('Tournament_member_doubles/Info/', tournament_member_doubles.Tournament_member_doubles_Info),
    path('Tournament_member_doubles/Copy', tournament_member_doubles.Tournament_member_doubles_Copy),

]
