# pylint: disable=missing-module-docstring
import os
from os.path import join, basename

package_name = basename(os.path.dirname(os.path.realpath(__file__)))

os.environ['MODULES_PATH'] = join(os.getcwd(), package_name, 'modules')
os.environ['DATA_STRUCTURES_PATH'] = join(os.getcwd(), package_name, 'data_structures')
