c.ServerApp.jpserver_extensions = {
  'jupyterlab': True,
  'jupytery_auth': True,
  }

from jupytery_auth.authentication import github
c.ServerApp.login_handler_class=github.LoginHandler

c.LabApp.collaborative = True
