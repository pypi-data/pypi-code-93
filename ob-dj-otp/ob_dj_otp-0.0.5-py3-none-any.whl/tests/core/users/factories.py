import factory
from django.contrib.auth import get_user_model
from factory import DjangoModelFactory, Faker


class UserFactory(DjangoModelFactory):
    email = Faker("email")
    # TODO: Replace with Faker("phone_number") with valid seed/provider for phone format
    phone_number = factory.Sequence(lambda n: f"+9659900{n:04}")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    password = Faker(
        "password",
        length=42,
        special_chars=True,
        digits=True,
        upper_case=True,
        lower_case=True,
    ).generate(extra_kwargs={})

    class Meta:
        model = get_user_model()

    class Params:
        superuser = factory.Trait(is_superuser=True, is_staff=True)
