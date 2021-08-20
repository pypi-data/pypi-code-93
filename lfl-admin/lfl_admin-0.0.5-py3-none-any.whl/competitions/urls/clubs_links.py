from django.urls import path

from lfl_admin.competitions.views import clubs_links

urlpatterns = [

    path('Clubs_links/Fetch/', clubs_links.Clubs_links_Fetch),
    path('Clubs_links/Add', clubs_links.Clubs_links_Add),
    path('Clubs_links/Update', clubs_links.Clubs_links_Update),
    path('Clubs_links/Remove', clubs_links.Clubs_links_Remove),
    path('Clubs_links/Lookup/', clubs_links.Clubs_links_Lookup),
    path('Clubs_links/Info/', clubs_links.Clubs_links_Info),
    path('Clubs_links/Copy', clubs_links.Clubs_links_Copy),

]
