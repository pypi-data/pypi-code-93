from django.urls import path

from lfl_admin.test.views import todos

urlpatterns = [

    path( 'Todos/Fetch/' , todos.Todos_Fetch ) ,
    path( 'Todos/Add' , todos.Todos_Add ) ,
    path( 'Todos/Update' , todos.Todos_Update ) ,
    path( 'Todos/Remove' , todos.Todos_Remove ) ,
    path( 'Todos/Lookup/' , todos.Todos_Lookup ) ,
    path( 'Todos/Info/' , todos.Todos_Info ) ,
    path( 'Todos/Copy' , todos.Todos_Copy ) ,

]
