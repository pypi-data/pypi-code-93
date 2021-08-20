from django.urls import path

from lfl_admin.decor.views import menus

urlpatterns = [

    path('Menus/Fetch/', menus.Menus_Fetch),
    path('Menus/Add', menus.Menus_Add),
    path('Menus/Update', menus.Menus_Update),
    path('Menus/Remove', menus.Menus_Remove),
    path('Menus/Lookup/', menus.Menus_Lookup),
    path('Menus/Info/', menus.Menus_Info),
    path('Menus/Copy', menus.Menus_Copy),

]
