from django.urls import path

from lfl_admin.decor.views import news_links

urlpatterns = [

    path('News_links/Fetch/', news_links.News_links_Fetch),
    path('News_links/Add', news_links.News_links_Add),
    path('News_links/Update', news_links.News_links_Update),
    path('News_links/Remove', news_links.News_links_Remove),
    path('News_links/Lookup/', news_links.News_links_Lookup),
    path('News_links/Info/', news_links.News_links_Info),
    path('News_links/Copy', news_links.News_links_Copy),

]
