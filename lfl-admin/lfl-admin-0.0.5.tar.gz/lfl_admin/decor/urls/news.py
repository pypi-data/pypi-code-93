from django.urls import path

from lfl_admin.decor.views import news

urlpatterns = [

    path('News/Fetch/', news.News_Fetch),
    path('News/Add', news.News_Add),
    path('News/Update', news.News_Update),
    path('News/Remove', news.News_Remove),
    path('News/Lookup/', news.News_Lookup),
    path('News/Info/', news.News_Info),
    path('News/Copy', news.News_Copy),

]
