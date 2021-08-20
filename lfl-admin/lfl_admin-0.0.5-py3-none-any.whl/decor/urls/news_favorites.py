from django.urls import path

from lfl_admin.decor.views import news_favorites

urlpatterns = [

    path('News_favorites/Fetch/', news_favorites.News_favorites_Fetch),
    path('News_favorites/Add', news_favorites.News_favorites_Add),
    path('News_favorites/Update', news_favorites.News_favorites_Update),
    path('News_favorites/Remove', news_favorites.News_favorites_Remove),
    path('News_favorites/Lookup/', news_favorites.News_favorites_Lookup),
    path('News_favorites/Info/', news_favorites.News_favorites_Info),
    path('News_favorites/Copy', news_favorites.News_favorites_Copy),

]
