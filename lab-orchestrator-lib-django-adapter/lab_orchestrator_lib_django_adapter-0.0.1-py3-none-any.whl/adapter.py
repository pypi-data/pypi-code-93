"""This module contains adapters for the lab_orchestrator_lib.

There are two representations of the data classes. One is called library objects (LibModelType) and the other is called
database objects (ModelType). The library objects are the objects that are used in the library and the database objects
are added in the models module and used to store the library objects in a database for persistent storage.

The adapters are used to store the library objects in a database in a django project. To achieve this the adapter
classes needs to implement several methods for example to retrieve and delete objects. These methods are then used in
the lab_orchestrator_lib and in the django project. For example if you want to start a lab instance, you need to use a
controller from the lab_orchestrator_lib and this controller will use the methods defined in the below adapters to save
a lab_instance object in the database.
"""
from typing import List, Type, Any, Dict, TypeVar, Generic

from django.contrib.auth import get_user_model

from lab_orchestrator_lib.database import adapter
from lab_orchestrator_lib.model.model import DockerImage, Identifier, LabInstance, Lab, User

from lab_orchestrator_lib_django_adapter.models import DockerImageModel, LabModel, LabInstanceModel


class UserDjangoAdapter(adapter.UserAdapterInterface):
    def get_all(self) -> List[User]:
        """Gets all database objects from the database and returns them as library objects."""
        return self.to_obj_list(get_user_model().objects.all())

    def get(self, identifier: Identifier) -> User:
        """Gets one specific database object and returns it as library object."""
        return self.to_obj(get_user_model().objects.get(pk=identifier))

    def to_obj(self, mod: get_user_model()) -> User:
        """Converts the database object into an object of the library."""
        return User(mod.id)

    def to_obj_list(self, mods: List[get_user_model()]) -> List[User]:
        """Converts a list of database objects into a list of objects of the library."""
        return [self.to_obj(mod) for mod in mods]


ModelType = TypeVar('ModelType', DockerImageModel, LabModel, LabInstanceModel)  # subclasses of models.Model
LibModelType = TypeVar('LibModelType', DockerImage, Lab, LabInstance)  # subclasses of Model


class DjangoAdapter(Generic[ModelType, LibModelType]):
    """Generic base class that implements the methods needed to save, retrieve and delete objects from the django
    database.

    To use this generic adapter to implement an interface you need to extend first this DjangoAdapter and then the
    AdapterInterface. Example `class DjangoDockerImageAdapter(DjangoAdapter, adapter.DockerImageAdapterInterface)`.
    With this sequence the generic methods will overwrite the interface methods.

    You also need to implement the methods `to_obj` and `to_model` which convert a database object to a library object
    on one side and the other way round on the other side and the method `create` which contains specific parts, that
    can't be abstracted.
    """
    def __init__(self, cls: Type[ModelType]):
        self.cls = cls

    def to_obj(self, mod: ModelType) -> LibModelType:
        """Converts the database object into an object of the library."""
        raise NotImplementedError()

    def to_model(self, obj: LibModelType) -> ModelType:
        """Converts the object of the library into an database object."""
        raise NotImplementedError()

    def to_obj_list(self, mods: List[ModelType]) -> List[LibModelType]:
        """Converts a list of database objects into a list of objects of the library."""
        return [self.to_obj(mod) for mod in mods]

    def to_model_list(self, objs: List[LibModelType]) -> List[ModelType]:
        """Converts a list of database objects into a list of objects of the library."""
        return [self.to_model(obj) for obj in objs]

    def get_all(self) -> List[LibModelType]:
        """Gets all database objects from the database and returns them as library objects."""
        return self.to_obj_list(self.cls.objects.all())

    def get(self, identifier: Identifier) -> LibModelType:
        """Gets one specific database object and returns it as library object."""
        return self.to_obj(self.cls.objects.get(pk=identifier))

    def get_by_attr(self, attr: str, value: Any) -> LibModelType:
        """Gets one specific database object by attribute and value combination and returns it as library object."""
        return self.to_obj(self.cls.objects.get(**{attr: value}))

    def filter(self, **kwargs: Dict[str, Any]) -> LibModelType:
        """Filters one specific database object by a combination of attributes and values and returns it as library
        object."""
        return self.to_obj(self.cls.objects.filter(**kwargs).first())

    def delete(self, identifier: Identifier) -> None:
        """Deletes the database object with the given identifier."""
        self.cls.objects.get(pk=identifier).delete()

    def save(self, identifier: Identifier, data: Dict[str, Any]) -> LibModelType:
        """Sets the data as new content of the object with the given identifier."""
        mod = self.cls.objects.get(pk=identifier)
        mod.__dict__ = data
        mod.save()
        return self.to_obj(mod)


class DockerImageDjangoAdapter(DjangoAdapter, adapter.DockerImageAdapterInterface):
    def __init__(self):
        super().__init__(DockerImageModel)

    def create(self, name: str, description: str, url: str) -> DockerImage:
        return self.to_obj(self.cls.objects.create(name=name, description=description, url=url))

    def to_model(self, obj: DockerImage) -> DockerImageModel:
        return DockerImageModel(**obj.__dict__)

    def to_obj(self, mod: DockerImageModel) -> DockerImage:
        return DockerImage(**mod.__dict__)


class LabDjangoAdapter(DjangoAdapter, adapter.LabAdapterInterface):
    def __init__(self):
        super().__init__(LabModel)

    def create(self, name: str, namespace_prefix: str, description: str, docker_image_id: Identifier,
               docker_image_name: str) -> Lab:
        return self.to_obj(self.cls.objects.create(
            name=name, namespace_prefix=namespace_prefix, description=description, docker_image_id=docker_image_id,
            docker_image_name=docker_image_name
        ))

    def to_model(self, obj: Lab) -> LabModel:
        return LabModel(**obj.__dict__)

    def to_obj(self, mod: LabModel) -> Lab:
        return Lab(**mod.__dict__)


class LabInstanceDjangoAdapter(DjangoAdapter, adapter.LabInstanceAdapterInterface):
    def __init__(self):
        super().__init__(DockerImageModel)

    def create(self, lab_id: Identifier, user_id: Identifier) -> LabInstance:
        return self.to_obj(self.cls.objects.create(lab_id=lab_id, user_id=user_id))

    def to_model(self, obj: LabInstance) -> LabInstanceModel:
        return LabInstanceModel(**obj.__dict__)

    def to_obj(self, mod: LabInstanceModel) -> LabInstance:
        return LabInstance(**mod.__dict__)
