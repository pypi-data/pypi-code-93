from django.urls import path

from lfl_admin.competitions.views import leagues_links

urlpatterns = [

    path('Leagues_links/Fetch/', leagues_links.Leagues_links_Fetch),
    path('Leagues_links/Add', leagues_links.Leagues_links_Add),
    path('Leagues_links/Update', leagues_links.Leagues_links_Update),
    path('Leagues_links/Remove', leagues_links.Leagues_links_Remove),
    path('Leagues_links/Lookup/', leagues_links.Leagues_links_Lookup),
    path('Leagues_links/Info/', leagues_links.Leagues_links_Info),
    path('Leagues_links/Copy', leagues_links.Leagues_links_Copy),

]
