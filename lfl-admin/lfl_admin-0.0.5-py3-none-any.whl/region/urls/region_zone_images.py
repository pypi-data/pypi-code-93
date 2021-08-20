from django.urls import path

from lfl_admin.region.views import region_zone_images

urlpatterns = [

    path('Region_zone_images/Fetch/', region_zone_images.Region_zone_images_Fetch),
    path('Region_zone_images/Add', region_zone_images.Region_zone_images_Add),
    path('Region_zone_images/Update', region_zone_images.Region_zone_images_Update),
    path('Region_zone_images/Remove', region_zone_images.Region_zone_images_Remove),
    path('Region_zone_images/Lookup/', region_zone_images.Region_zone_images_Lookup),
    path('Region_zone_images/Info/', region_zone_images.Region_zone_images_Info),
    path('Region_zone_images/Copy', region_zone_images.Region_zone_images_Copy),

]
