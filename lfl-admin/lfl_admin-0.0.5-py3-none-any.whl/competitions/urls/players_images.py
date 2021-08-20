from django.urls import path

from lfl_admin.competitions.views import players_images

urlpatterns = [

    path('Players_images/Fetch/', players_images.Players_images_Fetch),
    path('Players_images/Add', players_images.Players_images_Add),
    path('Players_images/Update', players_images.Players_images_Update),
    path('Players_images/Remove', players_images.Players_images_Remove),
    path('Players_images/Lookup/', players_images.Players_images_Lookup),
    path('Players_images/Info/', players_images.Players_images_Info),
    path('Players_images/Copy', players_images.Players_images_Copy),

]
