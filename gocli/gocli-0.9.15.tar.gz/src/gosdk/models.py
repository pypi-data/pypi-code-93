# common.py - models that are shared across versions.

from specd.sdk import BaseModel


class AnnotationList(BaseModel):

    # Set of keys that are NOT annotations. New top-level keys must be added.
    META_KEYS = {"errors", "is_created", "additionalProperties", "normalized"}

    def get_annotation(self, key):
        obj_dict = getattr(self, key, None)
        if obj_dict:
            return self.instantiate(self.definitions.Annotation, obj_dict)

    def iter_annotations(self):
        for key in self:
            if key not in AnnotationList.META_KEYS:
                yield self.get_annotation(key)


class AnnotationMatchList(BaseModel):
    # Set of keys that are NOT annotations. New top-level keys must be added.
    META_KEYS = {"errors", "is_created", "additionalProperties", "normalized"}

    def get_annotation(self, key):
        obj_dict = getattr(self, key, None)
        if obj_dict:
            return self.instantiate(self.definitions.AnnotationMatch, obj_dict)

    def iter_annotations(self):
        for key in self:
            if key not in AnnotationMatchList.META_KEYS:
                yield self.get_annotation(key)


class VariantInterpretationResponse(BaseModel):

    # set of keys that are NOT part of the variant interpretations response
    META_KEYS = {"errors", "additionalProperties"}

    def get_var_int_data(self, key):
        obj_dict = getattr(self, key, None)
        if obj_dict:
            return self.instantiate(
                self.definitions.VariantInterpretationSingleResponse, obj_dict
            )

    def iter_var_int_data(self):
        for key in self:
            if key not in VariantInterpretationResponse.META_KEYS:
                yield self.get_var_int_data(key)
