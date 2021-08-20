from django.urls import path

from lfl_admin.region.views import cities

urlpatterns = [

    path('Cities/Fetch/', cities.Cities_Fetch),
    path('Cities/Add', cities.Cities_Add),
    path('Cities/Update', cities.Cities_Update),
    path('Cities/Remove', cities.Cities_Remove),
    path('Cities/Lookup/', cities.Cities_Lookup),
    path('Cities/Info/', cities.Cities_Info),
    path('Cities/Copy', cities.Cities_Copy),

]
