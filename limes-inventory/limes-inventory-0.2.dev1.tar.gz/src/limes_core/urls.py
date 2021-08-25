from django.urls import path
from django.urls.resolvers import URLPattern

from limes_common.models.network.endpoints import ServerEndpoint as Endpoint
from limes_common import config
from . import views

def genPath(ep: Endpoint) -> URLPattern:
    epName = str(ep)
    return path('%s/%s' % (config.SERVER_API_VER, ep.Path), views.__dict__[epName.title()], name=epName)

# urlpatterns = [
#     path('%s/login' % VER, views.Login, name='login'),
#     path('%s/authenticate' % VER, views.Authenticate, name='authenticate'),
# ]

urlpatterns = list(map(genPath, Endpoint))
