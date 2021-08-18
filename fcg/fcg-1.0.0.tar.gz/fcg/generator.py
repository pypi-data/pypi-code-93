# -*- coding:utf-8 -*-
# @Time     : 2021/8/18 11:48
# @Author   : Charon.
import re
import sys
import os
from docopt import docopt
from fcg.version import __version__

actions = """
from core.actions._base import SingleAction
from core.models._all import ${resource} as Model
from core.repositories.${resource_name} import ${resource}Repository


class ${resource}Action(SingleAction):
    path = '/'

    def init_handle(self):
        self.handle = self.repository.all
"""

models = """
from . import *  # noqa
from sqlalchemy import CHAR, Column, DECIMAL, DateTime, Enum, Index, LargeBinary, String, TIMESTAMP, Text, text
from sqlalchemy.dialects.mysql import BIGINT, INTEGER, MEDIUMINT, SET, TINYINT, VARCHAR, YEAR
from sqlalchemy.sql.sqltypes import NullType
from sqlalchemy.ext.declarative import declarative_base

from core.models._base import BaseModel
Base = BaseModel
metadata = Base.metadata


class ${resource}(Base):
    pass

"""

repositories = """
from core.repositories._base import BaseRepository
import typing as tp


class ${resource}Repository(BaseRepository):
    def all(self) -> tp.Any:
        return {}
        """

resources = """
from core.actions.${resource_name} import ${resource}Action
from core.models.${resource_name} import ${resource} as Model
from core.repositories._base import CRUDRepository
from core.repositories.${resource_name} import ${resource}Repository
from core.resources._base import BaseResource
from core.transformers.${resource_name} import ${resource} as Transformer


class ${resource}Resource(BaseResource):
    name = '${resource_name}'
    name_doc = ''
    path = '/${resource_name}s'

    Actions = [${resource}Action]

    repository = ${resource}Repository()
    Transformer = Transformer

    # create_Validator = Validator1
    # partial_update_Validator = Validator2


resource = ${resource}Resource().register_resource()
"""

transformers = """
import typing as tp
from core.transformers._base import OrmTransformer

class ${resource}(OrmTransformer):
    pass
"""

validators = """
import typing as tp
from core.validators._base import BaseValidator


class ${resource}Validator(BaseValidator):
    pass
"""


def main():
    try:
        resource_name = sys.argv[1]
    except:
        raise Exception('need a resource name')

    try:
        dir = sys.argv[2]
        if 'core' in dir:
            dir_ = dir
        else:
            raise Exception('need a correct absolute path')
    except:
        if 'core' in os.getcwd():
            dir_ = os.getcwd()
        elif 'core' in os.listdir():
            os.chdir('core')
            dir_ = os.getcwd()
        else:
            raise Exception('need a correct absolute path')

    resource = resource_name.title()

    template_dict = {'actions': actions,
                     'models': models,
                     'repositories': repositories,
                     'resources': resources,
                     'transformers': transformers,
                     'validators': validators
                     }

    for template_name, template in template_dict.items():
        template = re.sub(r'\$\{resource\}', resource, str(template))
        template_ = re.sub(r'\$\{resource_name\}', resource_name, str(template))
        with open(dir_+fr'\{template_name}\{resource_name}.py', 'w') as w:
            w.write(template_)


if __name__ == '__main__':
    main()
