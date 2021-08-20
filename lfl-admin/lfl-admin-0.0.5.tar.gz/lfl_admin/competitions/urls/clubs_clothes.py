from django.urls import path

from lfl_admin.competitions.views import clubs_clothes

urlpatterns = [

    path('Clubs_clothes/Fetch/', clubs_clothes.Clubs_clothes_Fetch),
    path('Clubs_clothes/Add', clubs_clothes.Clubs_clothes_Add),
    path('Clubs_clothes/Update', clubs_clothes.Clubs_clothes_Update),
    path('Clubs_clothes/Remove', clubs_clothes.Clubs_clothes_Remove),
    path('Clubs_clothes/Lookup/', clubs_clothes.Clubs_clothes_Lookup),
    path('Clubs_clothes/Info/', clubs_clothes.Clubs_clothes_Info),
    path('Clubs_clothes/Copy', clubs_clothes.Clubs_clothes_Copy),

]
