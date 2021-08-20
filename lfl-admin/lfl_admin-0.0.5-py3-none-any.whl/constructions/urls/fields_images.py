from django.urls import path

from lfl_admin.constructions.views import fields_images

urlpatterns = [

    path('Fields_images/Fetch/', fields_images.Fields_images_Fetch),
    path('Fields_images/Add', fields_images.Fields_images_Add),
    path('Fields_images/Update', fields_images.Fields_images_Update),
    path('Fields_images/Remove', fields_images.Fields_images_Remove),
    path('Fields_images/Lookup/', fields_images.Fields_images_Lookup),
    path('Fields_images/Info/', fields_images.Fields_images_Info),
    path('Fields_images/Copy', fields_images.Fields_images_Copy),

]
