from django.urls import path

from lfl_admin.user_ext.views import contacts

urlpatterns = [

    path('Contacts/Fetch/', contacts.Contacts_Fetch),
    path('Contacts/Add', contacts.Contacts_Add),
    path('Contacts/Update', contacts.Contacts_Update),
    path('Contacts/Remove', contacts.Contacts_Remove),
    path('Contacts/Lookup/', contacts.Contacts_Lookup),
    path('Contacts/Info/', contacts.Contacts_Info),
    path('Contacts/Copy', contacts.Contacts_Copy),

]
