from django.urls import path

from lfl_admin.competitions.views import club_admins

urlpatterns = [

    path('Club_admins/Fetch/', club_admins.Club_admins_Fetch),
    path('Club_admins/Add', club_admins.Club_admins_Add),
    path('Club_admins/Update', club_admins.Club_admins_Update),
    path('Club_admins/Remove', club_admins.Club_admins_Remove),
    path('Club_admins/Lookup/', club_admins.Club_admins_Lookup),
    path('Club_admins/Info/', club_admins.Club_admins_Info),
    path('Club_admins/Copy', club_admins.Club_admins_Copy),

]
