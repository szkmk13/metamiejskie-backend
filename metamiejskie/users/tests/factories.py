from factory import Faker, SubFactory
from factory.django import DjangoModelFactory

from metamiejskie.users.models import User, Quest, DailyQuest


class UserFactory(DjangoModelFactory):
    username = Faker("user_name")

    class Meta:
        model = User


class QuestFactory(DjangoModelFactory):
    title = Faker("sentence")
    description = Faker("paragraph")
    duration = Faker("time_delta")

    class Meta:
        model = Quest


class DailyQuestFactory(DjangoModelFactory):
    # created_at = Faker("now")
    quest = SubFactory(QuestFactory)
    user = SubFactory(UserFactory)

    class Meta:
        model = DailyQuest
