from django.urls import path

from lfl_admin.decor.views import banners

urlpatterns = [

    path('Banners/Fetch/', banners.Banners_Fetch),
    path('Banners/Add', banners.Banners_Add),
    path('Banners/Update', banners.Banners_Update),
    path('Banners/Remove', banners.Banners_Remove),
    path('Banners/Lookup/', banners.Banners_Lookup),
    path('Banners/Info/', banners.Banners_Info),
    path('Banners/Copy', banners.Banners_Copy),

]
