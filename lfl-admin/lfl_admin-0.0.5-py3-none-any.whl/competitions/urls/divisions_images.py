from django.urls import path

from lfl_admin.competitions.views import divisions_images

urlpatterns = [

    path('Divisions_images/Fetch/', divisions_images.Divisions_images_Fetch),
    path('Divisions_images/Add', divisions_images.Divisions_images_Add),
    path('Divisions_images/Update', divisions_images.Divisions_images_Update),
    path('Divisions_images/Remove', divisions_images.Divisions_images_Remove),
    path('Divisions_images/Lookup/', divisions_images.Divisions_images_Lookup),
    path('Divisions_images/Info/', divisions_images.Divisions_images_Info),
    path('Divisions_images/Copy', divisions_images.Divisions_images_Copy),

]
