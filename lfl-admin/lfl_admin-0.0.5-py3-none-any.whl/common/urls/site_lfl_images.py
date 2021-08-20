from django.urls import path

from lfl_admin.common.views import site_lfl_images

urlpatterns = [

    path('Site_lfl_images/Fetch/', site_lfl_images.Site_lfl_images_Fetch),
    path('Site_lfl_images/Add', site_lfl_images.Site_lfl_images_Add),
    path('Site_lfl_images/Update', site_lfl_images.Site_lfl_images_Update),
    path('Site_lfl_images/Remove', site_lfl_images.Site_lfl_images_Remove),
    path('Site_lfl_images/Lookup/', site_lfl_images.Site_lfl_images_Lookup),
    path('Site_lfl_images/Info/', site_lfl_images.Site_lfl_images_Info),
    path('Site_lfl_images/Copy', site_lfl_images.Site_lfl_images_Copy),

]
