from django.urls import path

from lfl_admin.decor.views import menus_links

urlpatterns = [

    path('Menus_links/Fetch/', menus_links.Menus_links_Fetch),
    path('Menus_links/Add', menus_links.Menus_links_Add),
    path('Menus_links/Update', menus_links.Menus_links_Update),
    path('Menus_links/Remove', menus_links.Menus_links_Remove),
    path('Menus_links/Lookup/', menus_links.Menus_links_Lookup),
    path('Menus_links/Info/', menus_links.Menus_links_Info),
    path('Menus_links/Copy', menus_links.Menus_links_Copy),

]
