from django.urls import path

from lfl_admin.competitions.views import referees_images

urlpatterns = [

    path('Referees_images/Fetch/', referees_images.Referees_images_Fetch),
    path('Referees_images/Add', referees_images.Referees_images_Add),
    path('Referees_images/Update', referees_images.Referees_images_Update),
    path('Referees_images/Remove', referees_images.Referees_images_Remove),
    path('Referees_images/Lookup/', referees_images.Referees_images_Lookup),
    path('Referees_images/Info/', referees_images.Referees_images_Info),
    path('Referees_images/Copy', referees_images.Referees_images_Copy),

]
