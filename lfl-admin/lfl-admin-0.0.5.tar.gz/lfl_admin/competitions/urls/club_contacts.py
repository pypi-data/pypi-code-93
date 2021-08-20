from django.urls import path

from lfl_admin.competitions.views import club_contacts

urlpatterns = [

    path('Club_contacts/Fetch/', club_contacts.Club_contacts_Fetch),
    path('Club_contacts/Add', club_contacts.Club_contacts_Add),
    path('Club_contacts/Update', club_contacts.Club_contacts_Update),
    path('Club_contacts/Remove', club_contacts.Club_contacts_Remove),
    path('Club_contacts/Lookup/', club_contacts.Club_contacts_Lookup),
    path('Club_contacts/Info/', club_contacts.Club_contacts_Info),
    path('Club_contacts/Copy', club_contacts.Club_contacts_Copy),

]
