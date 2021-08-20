from django.urls import path

from lfl_admin.competitions.views import club_logo_history

urlpatterns = [

    path('Club_logo_history/Fetch/', club_logo_history.Club_logo_history_Fetch),
    path('Club_logo_history/Add', club_logo_history.Club_logo_history_Add),
    path('Club_logo_history/Update', club_logo_history.Club_logo_history_Update),
    path('Club_logo_history/Remove', club_logo_history.Club_logo_history_Remove),
    path('Club_logo_history/Lookup/', club_logo_history.Club_logo_history_Lookup),
    path('Club_logo_history/Info/', club_logo_history.Club_logo_history_Info),
    path('Club_logo_history/Copy', club_logo_history.Club_logo_history_Copy),

]
