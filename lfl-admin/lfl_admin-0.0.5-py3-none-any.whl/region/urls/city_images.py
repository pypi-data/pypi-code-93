from django.urls import path

from lfl_admin.region.views import city_images

urlpatterns = [

    path('City_images/Fetch/', city_images.City_images_Fetch),
    path('City_images/Add', city_images.City_images_Add),
    path('City_images/Update', city_images.City_images_Update),
    path('City_images/Remove', city_images.City_images_Remove),
    path('City_images/Lookup/', city_images.City_images_Lookup),
    path('City_images/Info/', city_images.City_images_Info),
    path('City_images/Copy', city_images.City_images_Copy),

]
