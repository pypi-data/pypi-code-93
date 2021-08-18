import os
import site

import constellate

constellate_path = os.path.abspath(constellate.__file__)

site_path = site.getusersitepackages()

alias = "tdm_client.pth"

with open(os.path.join(site_path, alias), "w") as of:
    of.write(constellate_path)
