from django.urls import path

from lfl_admin.competitions.views import calendar_images

urlpatterns = [

    path('Calendar_images/Fetch/', calendar_images.Calendar_images_Fetch),
    path('Calendar_images/Add', calendar_images.Calendar_images_Add),
    path('Calendar_images/Update', calendar_images.Calendar_images_Update),
    path('Calendar_images/Remove', calendar_images.Calendar_images_Remove),
    path('Calendar_images/Lookup/', calendar_images.Calendar_images_Lookup),
    path('Calendar_images/Info/', calendar_images.Calendar_images_Info),
    path('Calendar_images/Copy', calendar_images.Calendar_images_Copy),

]
