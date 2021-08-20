from django.urls import path

from lfl_admin.competitions.views import clubs_images

urlpatterns = [

    path('Clubs_images/Fetch/', clubs_images.Clubs_images_Fetch),
    path('Clubs_images/Add', clubs_images.Clubs_images_Add),
    path('Clubs_images/Update', clubs_images.Clubs_images_Update),
    path('Clubs_images/Remove', clubs_images.Clubs_images_Remove),
    path('Clubs_images/Lookup/', clubs_images.Clubs_images_Lookup),
    path('Clubs_images/Info/', clubs_images.Clubs_images_Info),
    path('Clubs_images/Copy', clubs_images.Clubs_images_Copy),

]
