from django.db import models

from w.django.models import AbstractCreatedUpdatedModel


class Author(models.Model):
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)


class Series(models.Model):
    name = models.CharField(max_length=128)


class Book(models.Model):
    name = models.CharField(max_length=128)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books")
    series = models.ForeignKey(
        Series, on_delete=models.CASCADE, related_name="books", blank=True, null=True
    )


class Character(models.Model):
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    books = models.ManyToManyField(Book, related_name="characters")


class AutoNowModel(AbstractCreatedUpdatedModel):
    pass
