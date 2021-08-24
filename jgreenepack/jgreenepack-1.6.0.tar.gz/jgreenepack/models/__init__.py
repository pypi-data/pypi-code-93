# flake8: noqa

# import all models into this package
# if you have many models here with many references from one model to another this may
# raise a RecursionError
# to avoid this, import only the models that you directly need like:
# from from jgreenepack.model.pet import Pet
# or import this package, but before doing it, use:
# import sys
# sys.setrecursionlimit(n)

from jgreenepack.model.error import Error
from jgreenepack.model.pet import Pet
from jgreenepack.model.pets import Pets
