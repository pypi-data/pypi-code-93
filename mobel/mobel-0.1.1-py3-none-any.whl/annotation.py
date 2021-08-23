from dataclasses import dataclass
from typing import Callable, Optional, Type, Union

from .common import ANNOTATION_DIR


class Annotation:

    def __new__(cls, f: Optional[Callable] = None, /, **kwargs):
        data_cls = dataclass(cls)
        setattr(data_cls, "name", data_cls.__name__)
        annotation_instance = super(Annotation, data_cls).__new__(cls)
        if f is None:
            return annotation_instance
        try:
            data_cls(**kwargs)
        except TypeError as e:
            raise TypeError("Annotation " + str(e)[11:])
        return annotation_instance(f)

    def __call__(self, f):
        if hasattr(f, ANNOTATION_DIR):
            getattr(f, ANNOTATION_DIR)[self.name] = self
        else:
            setattr(f, ANNOTATION_DIR, {self.name: self})
        return f


def hasAnnotation(f: Union[Callable, Type], annotation_name: str) -> bool:
    if not hasattr(f, ANNOTATION_DIR):
        return False
    return annotation_name in getattr(f, ANNOTATION_DIR)


def getAnnotation(f: Union[Callable, Type], annotation_name: str) -> Optional[Annotation]:
    if not hasattr(f, ANNOTATION_DIR):
        return None
    return getattr(f, ANNOTATION_DIR).get(annotation_name, None)
