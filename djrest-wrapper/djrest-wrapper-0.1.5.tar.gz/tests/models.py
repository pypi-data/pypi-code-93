from django.db import models
from djrest_wrapper.interfaces import BaseModel


class ExampleModel(BaseModel):
    text = models.CharField(max_length=10)

    
