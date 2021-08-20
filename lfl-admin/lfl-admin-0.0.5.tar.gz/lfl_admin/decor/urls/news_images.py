from django.urls import path

from lfl_admin.decor.views import news_images

urlpatterns = [

    path('News_images/Fetch/', news_images.News_images_Fetch),
    path('News_images/Add', news_images.News_images_Add),
    path('News_images/Update', news_images.News_images_Update),
    path('News_images/Remove', news_images.News_images_Remove),
    path('News_images/Lookup/', news_images.News_images_Lookup),
    path('News_images/Info/', news_images.News_images_Info),
    path('News_images/Copy', news_images.News_images_Copy),

]
