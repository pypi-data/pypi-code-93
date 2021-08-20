from django.urls import path

from lfl_admin.competitions.views import penalties

urlpatterns = [

    path('Penalties/Fetch/', penalties.Penalties_Fetch),
    path('Penalties/Add', penalties.Penalties_Add),
    path('Penalties/Update', penalties.Penalties_Update),
    path('Penalties/Remove', penalties.Penalties_Remove),
    path('Penalties/Lookup/', penalties.Penalties_Lookup),
    path('Penalties/Info/', penalties.Penalties_Info),
    path('Penalties/Copy', penalties.Penalties_Copy),

]
