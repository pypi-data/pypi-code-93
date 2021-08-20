from django.urls import path

from lfl_admin.competitions.views import club_histories

urlpatterns = [

    path('Club_histories/Fetch/', club_histories.Club_histories_Fetch),
    path('Club_histories/Add', club_histories.Club_histories_Add),
    path('Club_histories/Update', club_histories.Club_histories_Update),
    path('Club_histories/Remove', club_histories.Club_histories_Remove),
    path('Club_histories/Lookup/', club_histories.Club_histories_Lookup),
    path('Club_histories/Info/', club_histories.Club_histories_Info),
    path('Club_histories/Copy', club_histories.Club_histories_Copy),

]
