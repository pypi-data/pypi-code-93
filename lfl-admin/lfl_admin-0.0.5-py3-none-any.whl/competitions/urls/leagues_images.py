from django.urls import path

from lfl_admin.competitions.views import leagues_images

urlpatterns = [

    path('Leagues_images/Fetch/', leagues_images.Leagues_images_Fetch),
    path('Leagues_images/Add', leagues_images.Leagues_images_Add),
    path('Leagues_images/Update', leagues_images.Leagues_images_Update),
    path('Leagues_images/Remove', leagues_images.Leagues_images_Remove),
    path('Leagues_images/Lookup/', leagues_images.Leagues_images_Lookup),
    path('Leagues_images/Info/', leagues_images.Leagues_images_Info),
    path('Leagues_images/Copy', leagues_images.Leagues_images_Copy),

]
