from django.urls import path

from lfl_admin.decor.views import banners_type

urlpatterns = [

    path('Banners_type/Fetch/', banners_type.Banners_type_Fetch),
    path('Banners_type/Add', banners_type.Banners_type_Add),
    path('Banners_type/Update', banners_type.Banners_type_Update),
    path('Banners_type/Remove', banners_type.Banners_type_Remove),
    path('Banners_type/Lookup/', banners_type.Banners_type_Lookup),
    path('Banners_type/Info/', banners_type.Banners_type_Info),
    path('Banners_type/Copy', banners_type.Banners_type_Copy),

]
