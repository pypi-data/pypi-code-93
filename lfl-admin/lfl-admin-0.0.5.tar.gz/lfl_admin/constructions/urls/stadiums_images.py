from django.urls import path

from lfl_admin.constructions.views import stadiums_images

urlpatterns = [

    path('Stadiums_images/Fetch/', stadiums_images.Stadiums_images_Fetch),
    path('Stadiums_images/Add', stadiums_images.Stadiums_images_Add),
    path('Stadiums_images/Update', stadiums_images.Stadiums_images_Update),
    path('Stadiums_images/Remove', stadiums_images.Stadiums_images_Remove),
    path('Stadiums_images/Lookup/', stadiums_images.Stadiums_images_Lookup),
    path('Stadiums_images/Info/', stadiums_images.Stadiums_images_Info),
    path('Stadiums_images/Copy', stadiums_images.Stadiums_images_Copy),

]
