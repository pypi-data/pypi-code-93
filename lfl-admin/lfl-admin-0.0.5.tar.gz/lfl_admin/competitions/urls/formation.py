from django.urls import path

from lfl_admin.competitions.views import formation

urlpatterns = [

    path('Formation/Fetch/', formation.Formation_Fetch),
    path('Formation/Add', formation.Formation_Add),
    path('Formation/Update', formation.Formation_Update),
    path('Formation/Remove', formation.Formation_Remove),
    path('Formation/Lookup/', formation.Formation_Lookup),
    path('Formation/Info/', formation.Formation_Info),
    path('Formation/Copy', formation.Formation_Copy),

]
