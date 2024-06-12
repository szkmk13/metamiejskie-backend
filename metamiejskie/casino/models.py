import enum
from random import shuffle

from django.core.validators import MinValueValidator
from django.db import models

from metamiejskie.users.admin import User


# Create your models here.


class LinesEnum(enum.Enum):
    _3x3 = ""


class Symbol(models.Model):
    name = models.CharField(max_length=128)
    image = models.ImageField()
    weight = models.PositiveIntegerField(default=1,
                                         help_text="Weight of the symbol, the higher number the bigger chance of it rolling")
    value = models.PositiveIntegerField(default=1,
                                        help_text="Value of the symbol, if user rolls a line of them, this is the amount it'sgona be multiplied by")
    def __str__(self):
        return f"{self.name} weight:{self.weight} multiplier:{self.value}"

class Game(models.Model):
    name = models.CharField(max_length=50)
    # lines = models.PositiveIntegerField(default=1)
    symbols = models.ManyToManyField(to=Symbol, related_name='games')

    # for now lets assume its only 3x3 game with 3 winning lanes top mid and bottom

    #3x3 czy 3x5 czy 5x5
    @property
    def spins(self):
        return self.spin_set.count()

    def get_random_symbol(self):
        # total_weight = self.symbols.aggregate('weight')
        all_symbols = []
        # print(self.symbols.all())
        for symbol in self.symbols.all():
            for _ in range(symbol.weight):
                all_symbols.append(symbol)
        shuffle(all_symbols)
        return all_symbols[0]


    def run(self, user, chosen_lines, *args, **kwargs):
        result = []
        for _row in range(3):
            row_result = []
            for _col in range(3):
                row_result.append(self.get_random_symbol().id)
            result.append(row_result)
        print(result)
        Spin.objects.create(user=user, game=self,chosen_lines=chosen_lines)


class Spin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    won = models.BooleanField(default=False)
    chosen_lines = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=5, decimal_places=2, default=10, validators=[MinValueValidator(10)])


