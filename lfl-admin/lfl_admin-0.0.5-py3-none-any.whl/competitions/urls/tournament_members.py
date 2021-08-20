from django.urls import path

from lfl_admin.competitions.views import tournament_members

urlpatterns = [

    path('Tournament_members/Fetch/', tournament_members.Tournament_members_Fetch),
    path('Tournament_members/Add', tournament_members.Tournament_members_Add),
    path('Tournament_members/Update', tournament_members.Tournament_members_Update),
    path('Tournament_members/Remove', tournament_members.Tournament_members_Remove),
    path('Tournament_members/Lookup/', tournament_members.Tournament_members_Lookup),
    path('Tournament_members/Info/', tournament_members.Tournament_members_Info),
    path('Tournament_members/Copy', tournament_members.Tournament_members_Copy),

]
