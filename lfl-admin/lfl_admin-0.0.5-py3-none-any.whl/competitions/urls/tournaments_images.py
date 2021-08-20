from django.urls import path

from lfl_admin.competitions.views import tournaments_images

urlpatterns = [

    path('Tournaments_images/Fetch/', tournaments_images.Tournaments_images_Fetch),
    path('Tournaments_images/Add', tournaments_images.Tournaments_images_Add),
    path('Tournaments_images/Update', tournaments_images.Tournaments_images_Update),
    path('Tournaments_images/Remove', tournaments_images.Tournaments_images_Remove),
    path('Tournaments_images/Lookup/', tournaments_images.Tournaments_images_Lookup),
    path('Tournaments_images/Info/', tournaments_images.Tournaments_images_Info),
    path('Tournaments_images/Copy', tournaments_images.Tournaments_images_Copy),

]
