from django.urls import path

from lfl_admin.decor.views import news_start_block_tournament

urlpatterns = [

    path('News_start_block_tournament/Fetch/', news_start_block_tournament.News_start_block_tournament_Fetch),
    path('News_start_block_tournament/Add', news_start_block_tournament.News_start_block_tournament_Add),
    path('News_start_block_tournament/Update', news_start_block_tournament.News_start_block_tournament_Update),
    path('News_start_block_tournament/Remove', news_start_block_tournament.News_start_block_tournament_Remove),
    path('News_start_block_tournament/Lookup/', news_start_block_tournament.News_start_block_tournament_Lookup),
    path('News_start_block_tournament/Info/', news_start_block_tournament.News_start_block_tournament_Info),
    path('News_start_block_tournament/Copy', news_start_block_tournament.News_start_block_tournament_Copy),

]
