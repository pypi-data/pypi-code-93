from django.urls import path

from lfl_admin.decor.views import menu_type

urlpatterns = [

    path('Menu_type/Fetch/', menu_type.Menu_type_Fetch),
    path('Menu_type/Add', menu_type.Menu_type_Add),
    path('Menu_type/Update', menu_type.Menu_type_Update),
    path('Menu_type/Remove', menu_type.Menu_type_Remove),
    path('Menu_type/Lookup/', menu_type.Menu_type_Lookup),
    path('Menu_type/Info/', menu_type.Menu_type_Info),
    path('Menu_type/Copy', menu_type.Menu_type_Copy),

]
