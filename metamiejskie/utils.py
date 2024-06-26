from factory import Faker, SubFactory
from factory.django import DjangoModelFactory
from rest_framework import status
from rest_framework.exceptions import APIException

from metamiejskie.users.models import User, Quest, DailyQuest, Variables


class DetailException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "A server error occurred."

    def __init__(self, detail, field="detail", status_code=None):
        if status_code is None:
            self.status_code = status_code
        if detail is not None:
            self.detail = {field: detail}
        else:
            self.detail = {"detail": self.default_detail}


class VariableFactory(DjangoModelFactory):
    name = Faker("word")
    value = Faker("pyint")

    class Meta:
        model = Variables


def variables_setup():
    VariableFactory(name="DAILY_COINS", value=10)
    VariableFactory(name="daily_quest_points", value=10)
    VariableFactory(name="daily_quest_coins", value=100)
