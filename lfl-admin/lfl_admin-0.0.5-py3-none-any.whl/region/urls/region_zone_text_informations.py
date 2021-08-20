from django.urls import path

from lfl_admin.region.views import region_zone_text_informations

urlpatterns = [

    path('Region_zone_text_informations/Fetch/', region_zone_text_informations.Region_zone_text_informations_Fetch),
    path('Region_zone_text_informations/Add', region_zone_text_informations.Region_zone_text_informations_Add),
    path('Region_zone_text_informations/Update', region_zone_text_informations.Region_zone_text_informations_Update),
    path('Region_zone_text_informations/Remove', region_zone_text_informations.Region_zone_text_informations_Remove),
    path('Region_zone_text_informations/Lookup/', region_zone_text_informations.Region_zone_text_informations_Lookup),
    path('Region_zone_text_informations/Info/', region_zone_text_informations.Region_zone_text_informations_Info),
    path('Region_zone_text_informations/Copy', region_zone_text_informations.Region_zone_text_informations_Copy),

]
