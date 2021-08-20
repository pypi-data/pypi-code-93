from django.urls import path

from lfl_admin.competitions.views import divisions

urlpatterns = [

    path('Divisions/Fetch/', divisions.Divisions_Fetch),
    path('Divisions/Add', divisions.Divisions_Add),
    path('Divisions/Update', divisions.Divisions_Update),
    path('Divisions/Remove', divisions.Divisions_Remove),
    path('Divisions/Lookup/', divisions.Divisions_Lookup),
    path('Divisions/Info/', divisions.Divisions_Info),
    path('Divisions/Copy', divisions.Divisions_Copy),

]
