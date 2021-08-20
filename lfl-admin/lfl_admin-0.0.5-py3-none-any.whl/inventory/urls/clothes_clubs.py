from django.urls import path

from lfl_admin.inventory.views import clothes_clubs

urlpatterns = [

    path('Clothes_clubs/Fetch/', clothes_clubs.Clothes_clubs_Fetch),
    path('Clothes_clubs/Add', clothes_clubs.Clothes_clubs_Add),
    path('Clothes_clubs/Update', clothes_clubs.Clothes_clubs_Update),
    path('Clothes_clubs/Remove', clothes_clubs.Clothes_clubs_Remove),
    path('Clothes_clubs/Lookup/', clothes_clubs.Clothes_clubs_Lookup),
    path('Clothes_clubs/Info/', clothes_clubs.Clothes_clubs_Info),
    path('Clothes_clubs/Copy', clothes_clubs.Clothes_clubs_Copy),

]
