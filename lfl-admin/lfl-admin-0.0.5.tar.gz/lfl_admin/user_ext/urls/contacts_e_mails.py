from django.urls import path

from lfl_admin.user_ext.views import contacts_e_mails

urlpatterns = [

    path('Contacts_e_mails/Fetch/', contacts_e_mails.Contacts_e_mails_Fetch),
    path('Contacts_e_mails/Add', contacts_e_mails.Contacts_e_mails_Add),
    path('Contacts_e_mails/Update', contacts_e_mails.Contacts_e_mails_Update),
    path('Contacts_e_mails/Remove', contacts_e_mails.Contacts_e_mails_Remove),
    path('Contacts_e_mails/Lookup/', contacts_e_mails.Contacts_e_mails_Lookup),
    path('Contacts_e_mails/Info/', contacts_e_mails.Contacts_e_mails_Info),
    path('Contacts_e_mails/Copy', contacts_e_mails.Contacts_e_mails_Copy),

]
