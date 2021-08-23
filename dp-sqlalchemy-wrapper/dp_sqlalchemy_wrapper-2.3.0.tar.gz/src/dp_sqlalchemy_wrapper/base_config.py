from abc import ABC, abstractmethod
from typing import List



class UnsetRequiredConfigPropertyException(Exception):
    def __init__(self, unset_required_properties: List[str], config_cls: type) -> None:
        err_msg = f"In {config_cls.__name__}, the following required properties are not set: {unset_required_properties}"
        super().__init__(err_msg)
        self.unset_required_properties = unset_required_properties

class UnsetConfigProperty:
    pass


class BaseConfig(ABC):
    """
    Simple Configuration via Python Class, for more complicated and typesafe configuration settings
    consider usage of https://github.com/crdoconnor/strictyaml
    """

    @classmethod
    @abstractmethod
    def get_required_properties(cls) -> List[str]:
        pass 


    @classmethod
    def validate(cls):
        """Validate whether all required properties are set in current class.
           Note, that no further property checks (type etc.) are performed

        Raises:
            UnsetRequiredConfigPropertyException: 

        Returns:
            [bool]: [if no exception is raised, return True]
        """
        unset_required_properties: List[str] = []
        for property in cls.get_required_properties():
            if not hasattr(cls, property):
                unset_required_properties.append(property)
            else:
                if getattr(cls, property) is UnsetConfigProperty:
                     unset_required_properties.append(property)

        
        if unset_required_properties:
            raise UnsetRequiredConfigPropertyException(unset_required_properties, cls)
        else:
            return True


class BaseDBConfig(BaseConfig):
    db_url = UnsetConfigProperty

    @classmethod
    def get_required_properties(cls) -> List[str]:
        return ["db_url"]