from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from metamiejskie.users.models import User, Quest, DailyQuest, Variables


class VariableFactory(DjangoModelFactory):
    name = Faker("word")
    value = Faker("pyint")

    class Meta:
        model = Variables


def variables_setup():
    VariableFactory(name="DAILY_COINS", value=10)
    VariableFactory(name="daily_quest_points", value=10)
    VariableFactory(name="daily_quest_coins", value=100)
