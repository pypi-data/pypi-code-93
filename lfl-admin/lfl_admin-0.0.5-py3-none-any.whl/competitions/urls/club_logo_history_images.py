from django.urls import path

from lfl_admin.competitions.views import club_logo_history_images

urlpatterns = [

    path('Club_logo_history_images/Fetch/', club_logo_history_images.Club_logo_history_images_Fetch),
    path('Club_logo_history_images/Add', club_logo_history_images.Club_logo_history_images_Add),
    path('Club_logo_history_images/Update', club_logo_history_images.Club_logo_history_images_Update),
    path('Club_logo_history_images/Remove', club_logo_history_images.Club_logo_history_images_Remove),
    path('Club_logo_history_images/Lookup/', club_logo_history_images.Club_logo_history_images_Lookup),
    path('Club_logo_history_images/Info/', club_logo_history_images.Club_logo_history_images_Info),
    path('Club_logo_history_images/Copy', club_logo_history_images.Club_logo_history_images_Copy),

]
