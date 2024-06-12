from factory.django import DjangoModelFactory

from metamiejskie.users.models import User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
