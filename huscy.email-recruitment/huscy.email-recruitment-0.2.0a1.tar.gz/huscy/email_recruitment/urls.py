from huscy.email_recruitment import views
from huscy.projects.urls import project_router


project_router.register('invitationemails', views.InvitationEMailViewSet,
                        basename='invitationemail')
project_router.register('reminderemails', views.ReminderEMailViewSet, basename='reminderemail')


urlpatterns = project_router.urls
