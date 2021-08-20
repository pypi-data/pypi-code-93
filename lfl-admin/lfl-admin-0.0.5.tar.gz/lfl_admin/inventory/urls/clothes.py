from django.urls import path

from lfl_admin.inventory.views import clothes

urlpatterns = [

    path('Clothes/Fetch/', clothes.Clothes_Fetch),
    path('Clothes/Add', clothes.Clothes_Add),
    path('Clothes/Update', clothes.Clothes_Update),
    path('Clothes/Remove', clothes.Clothes_Remove),
    path('Clothes/Lookup/', clothes.Clothes_Lookup),
    path('Clothes/Info/', clothes.Clothes_Info),
    path('Clothes/Copy', clothes.Clothes_Copy),

]
