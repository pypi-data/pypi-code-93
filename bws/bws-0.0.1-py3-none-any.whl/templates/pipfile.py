template = """
[[source]]
url = "https://pypi.org/simple"
verify_ssl = true
name = "pypi"

[packages]
#bws = "==0.0.7"
PyMySQL = "~=0.9.3"
Flask-SQLAlchemy = "~=2.4.1"
SQLAlchemy = "~=1.3.11"
pyjwt = "*"


[dev-packages]
#[requires]
#python_version = "3.8"
autopep8 = "*"

[scripts]
web = "python web.py"
cmd = "python cmd.py"
migrate = "python migrate.py"
create_project = "python -m bws.cmd.create_project"
create_app = "python -m bws.cmd.create_app"
update_bws = "pip install --upgrade git+https://ms-deploy:t9s6CVkAPZQjDuq7qWFq@git.maujagroup.com/ms/core.git#egg=bws"

[packages.bws]
git = "https://ms-deploy:t9s6CVkAPZQjDuq7qWFq@git.maujagroup.com/ms/core.git"
"""