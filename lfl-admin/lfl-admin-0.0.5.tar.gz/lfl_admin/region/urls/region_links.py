from django.urls import path

from lfl_admin.region.views import region_links

urlpatterns = [

    path('Region_links/Fetch/', region_links.Region_links_Fetch),
    path('Region_links/Add', region_links.Region_links_Add),
    path('Region_links/Update', region_links.Region_links_Update),
    path('Region_links/Remove', region_links.Region_links_Remove),
    path('Region_links/Lookup/', region_links.Region_links_Lookup),
    path('Region_links/Info/', region_links.Region_links_Info),
    path('Region_links/Copy', region_links.Region_links_Copy),

]
