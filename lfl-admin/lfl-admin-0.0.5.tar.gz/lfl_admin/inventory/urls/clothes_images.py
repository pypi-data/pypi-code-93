from django.urls import path

from lfl_admin.inventory.views import clothes_images

urlpatterns = [

    path('Clothes_images/Fetch/', clothes_images.Clothes_images_Fetch),
    path('Clothes_images/Add', clothes_images.Clothes_images_Add),
    path('Clothes_images/Update', clothes_images.Clothes_images_Update),
    path('Clothes_images/Remove', clothes_images.Clothes_images_Remove),
    path('Clothes_images/Lookup/', clothes_images.Clothes_images_Lookup),
    path('Clothes_images/Info/', clothes_images.Clothes_images_Info),
    path('Clothes_images/Copy', clothes_images.Clothes_images_Copy),

]
