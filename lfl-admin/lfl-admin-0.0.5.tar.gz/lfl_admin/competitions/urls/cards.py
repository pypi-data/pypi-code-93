from django.urls import path

from lfl_admin.competitions.views import cards

urlpatterns = [

    path('Cards/Fetch/', cards.Cards_Fetch),
    path('Cards/Add', cards.Cards_Add),
    path('Cards/Update', cards.Cards_Update),
    path('Cards/Remove', cards.Cards_Remove),
    path('Cards/Lookup/', cards.Cards_Lookup),
    path('Cards/Info/', cards.Cards_Info),
    path('Cards/Copy', cards.Cards_Copy),

]
