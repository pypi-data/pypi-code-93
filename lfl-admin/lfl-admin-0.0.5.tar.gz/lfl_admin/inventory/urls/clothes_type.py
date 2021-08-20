from django.urls import path

from lfl_admin.inventory.views import clothes_type

urlpatterns = [

    path('Clothes_type/Fetch/', clothes_type.Clothes_type_Fetch),
    path('Clothes_type/Add', clothes_type.Clothes_type_Add),
    path('Clothes_type/Update', clothes_type.Clothes_type_Update),
    path('Clothes_type/Remove', clothes_type.Clothes_type_Remove),
    path('Clothes_type/Lookup/', clothes_type.Clothes_type_Lookup),
    path('Clothes_type/Info/', clothes_type.Clothes_type_Info),
    path('Clothes_type/Copy', clothes_type.Clothes_type_Copy),

]
