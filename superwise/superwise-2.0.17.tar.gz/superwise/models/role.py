""" This module implement Role model  """
from superwise.models.base import BaseModel


class Role(BaseModel):
    """ Role model class, model  for roles data """

    def __init__(
        self,
        id=None,
        task_type_id=None,
        is_nullable=None,
        description=None,
        internal_name=None,
        is_label=None,
        is_optional=None,
        role=None,
        value=None,
        **kwargs
    ):
        """
        constructer for Role class

        :param id:
        :param task_type_id:
        :param is_nullable:
        :param task_description:
        :param description:
        :param internal_name:
        :param is_label:
        :param is_optional:
        :param role:
        :param value:
        """
        self.task_type_id = task_type_id
        self.description = description
        self.internal_name = internal_name
        self.is_label = is_label
        self.is_optional = is_optional
        self.value = value
        self.is_nullable = is_nullable
        self.role = role
        self.id = id
