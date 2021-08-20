from django.urls import path

from isc_common.views import users_old_images

urlpatterns = [

    path('Users_old_images/Fetch/', users_old_images.Users_old_images_Fetch),
    path('Users_old_images/Add', users_old_images.Users_old_images_Add),
    path('Users_old_images/Update', users_old_images.Users_old_images_Update),
    path('Users_old_images/Remove', users_old_images.Users_old_images_Remove),
    path('Users_old_images/Lookup/', users_old_images.Users_old_images_Lookup),
    path('Users_old_images/Info/', users_old_images.Users_old_images_Info),
    path('Users_old_images/Copy', users_old_images.Users_old_images_Copy),

]
