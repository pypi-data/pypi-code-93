from django.urls import path

from lfl_admin.user_ext.views import contacts_phones

urlpatterns = [

    path('Contacts_phones/Fetch/', contacts_phones.Contacts_phones_Fetch),
    path('Contacts_phones/Add', contacts_phones.Contacts_phones_Add),
    path('Contacts_phones/Update', contacts_phones.Contacts_phones_Update),
    path('Contacts_phones/Remove', contacts_phones.Contacts_phones_Remove),
    path('Contacts_phones/Lookup/', contacts_phones.Contacts_phones_Lookup),
    path('Contacts_phones/Info/', contacts_phones.Contacts_phones_Info),
    path('Contacts_phones/Copy', contacts_phones.Contacts_phones_Copy),

]
