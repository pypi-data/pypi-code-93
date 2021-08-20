from django.urls import path

from lfl_admin.competitions.views import card_types

urlpatterns = [

    path('Card_types/Fetch/', card_types.Card_types_Fetch),
    path('Card_types/Add', card_types.Card_types_Add),
    path('Card_types/Update', card_types.Card_types_Update),
    path('Card_types/Remove', card_types.Card_types_Remove),
    path('Card_types/Lookup/', card_types.Card_types_Lookup),
    path('Card_types/Info/', card_types.Card_types_Info),
    path('Card_types/Copy', card_types.Card_types_Copy),

]
