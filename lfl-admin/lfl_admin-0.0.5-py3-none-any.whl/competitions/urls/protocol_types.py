from django.urls import path

from lfl_admin.competitions.views import protocol_types

urlpatterns = [

    path('Protocol_types/Fetch/', protocol_types.Protocol_types_Fetch),
    path('Protocol_types/Add', protocol_types.Protocol_types_Add),
    path('Protocol_types/Update', protocol_types.Protocol_types_Update),
    path('Protocol_types/Remove', protocol_types.Protocol_types_Remove),
    path('Protocol_types/Lookup/', protocol_types.Protocol_types_Lookup),
    path('Protocol_types/Info/', protocol_types.Protocol_types_Info),
    path('Protocol_types/Copy', protocol_types.Protocol_types_Copy),

]
