import enum
import itertools
from abc import abstractmethod
from random import shuffle

from django.core.validators import MinValueValidator
from django.db import models

from metamiejskie.users.admin import User


class GAMES(models.TextChoices):
    HIGH_CARD = "HighCard"
    ROULETTE = "Roulette"
    BLACK_JACK = "BlackJack"
    BELLS = "Bells"


class Symbol(models.Model):
    name = models.CharField(max_length=128)
    image = models.ImageField()
    weight = models.PositiveIntegerField(
        default=1, help_text="Weight of the symbol, the higher number the bigger chance of it rolling"
    )
    value = models.PositiveIntegerField(
        default=1,
        help_text="Value of the symbol, if user rolls a line of them, this is the amount it'sgona be multiplied by",
    )

    def __str__(self):
        return f"{self.name} weight:{self.weight} multiplier:{self.value}"


class Spin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.CharField(max_length=20, choices=GAMES.choices)
    time = models.DateTimeField(auto_now_add=True)

    has_won = models.BooleanField(default=False)
    chosen_lines = models.PositiveIntegerField(default=1)
    amount = models.IntegerField(validators=[MinValueValidator(1)])


class Game(models.Model):
    name = models.CharField(max_length=50, default="")

    def __str__(self):
        return self.name


class HighCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    last_card = models.CharField(max_length=20, default="")


class Roulette(Game):
    @staticmethod
    def play(user, chosen_lines, *args, **kwargs):
        return None


class BlackJack(Game):
    @staticmethod
    def play(user, chosen_lines, *args, **kwargs):
        return None


class Bells(Game):
    @staticmethod
    def play(user, chosen_lines, *args, **kwargs):
        return None
