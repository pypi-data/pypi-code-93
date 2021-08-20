from django.urls import path

from lfl_admin.constructions.views import stadiums

urlpatterns = [

    path('Stadiums/Fetch/', stadiums.Stadiums_Fetch),
    path('Stadiums/Add', stadiums.Stadiums_Add),
    path('Stadiums/Update', stadiums.Stadiums_Update),
    path('Stadiums/Remove', stadiums.Stadiums_Remove),
    path('Stadiums/Lookup/', stadiums.Stadiums_Lookup),
    path('Stadiums/Info/', stadiums.Stadiums_Info),
    path('Stadiums/Copy', stadiums.Stadiums_Copy),

]
