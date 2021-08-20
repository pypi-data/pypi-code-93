from django.urls import path

from lfl_admin.region.views import region_images

urlpatterns = [

    path('Region_images/Fetch/', region_images.Region_images_Fetch),
    path('Region_images/Add', region_images.Region_images_Add),
    path('Region_images/Update', region_images.Region_images_Update),
    path('Region_images/Remove', region_images.Region_images_Remove),
    path('Region_images/Lookup/', region_images.Region_images_Lookup),
    path('Region_images/Info/', region_images.Region_images_Info),
    path('Region_images/Copy', region_images.Region_images_Copy),

]
