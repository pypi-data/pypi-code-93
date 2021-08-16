from django.db import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from ..exceptions import apis as apiexp
from .basemodel import BaseModel


class BaseService(object):
    def __init__(self, model: BaseModel):
        if model != None:
            self.model = model
            self.fields = [f.name for f in model._meta.get_fields()]
            try:
                # id is a default field, so we should remove it
                self.fields.remove('id')
            except Exception as e:
                pass
        else:
            self.model: BaseModel = BaseModel
            self.fields = []
            raise TypeError

    def get_model_by_id(self, id):
        try:
            return self.model.objects.get(id=id)
        except ObjectDoesNotExist:
            raise apiexp.DoesNotExistsExp(f'{self.model.__name__} not found')

    def create_model(self, fields: dict):
        try:
           model = self.model.objects.get_or_create(**fields)
           return model[0]
        except IntegrityError:
            raise apiexp.DuplicateModelExp(
                f'This {self.model.__name__} is already exists.')

    def update_model_by_id(self, id, fields: dict):
        model: BaseModel = self.get_model_by_id(id)
        for field in self.fields:
            setattr(model, field, fields.get(field, getattr(model, field)))
        model.save()
        model.refresh_from_db()
        return model

    def retrieve_model_by_id(self, id):
        return self.get_model_by_id(id)

    def delete_model_by_id(self, id):
        model: BaseModel = self.get_model_by_id(id)
        model.delete()

    def list_model(self):
        return self.model.objects.all()
