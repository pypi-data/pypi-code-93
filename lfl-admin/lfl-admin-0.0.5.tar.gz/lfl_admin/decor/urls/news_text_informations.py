from django.urls import path

from lfl_admin.decor.views import news_text_informations

urlpatterns = [

    path('News_text_informations/Fetch/', news_text_informations.News_text_informations_Fetch),
    path('News_text_informations/Add', news_text_informations.News_text_informations_Add),
    path('News_text_informations/Update', news_text_informations.News_text_informations_Update),
    path('News_text_informations/Remove', news_text_informations.News_text_informations_Remove),
    path('News_text_informations/Lookup/', news_text_informations.News_text_informations_Lookup),
    path('News_text_informations/Info/', news_text_informations.News_text_informations_Info),
    path('News_text_informations/Copy', news_text_informations.News_text_informations_Copy),

]
