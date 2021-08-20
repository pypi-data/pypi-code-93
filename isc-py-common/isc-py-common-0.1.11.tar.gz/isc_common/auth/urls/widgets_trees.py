from django.urls import path
from isc_common.auth.views.widgets_trees import Widgets_trees_Fetch, Widgets_trees_Add, Widgets_trees_Update, Widgets_trees_Remove, Widgets_trees_Info, Widgets_trees_Lookup

urlpatterns = [

    path('Widgets_trees/Fetch/', Widgets_trees_Fetch),
    path('Widgets_trees/Add', Widgets_trees_Add),
    path('Widgets_trees/Update', Widgets_trees_Update),
    path('Widgets_trees/Remove', Widgets_trees_Remove),
    path('Widgets_trees/Lookup/', Widgets_trees_Lookup),
    path('Widgets_trees/Info/', Widgets_trees_Info),

]
