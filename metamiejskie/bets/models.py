from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from metamiejskie.users.models import User


class Bet(models.Model):
    started_by = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    total = models.IntegerField(default=100)

    label_1 = models.CharField(max_length=50, default="TAK")
    label_2 = models.CharField(max_length=50, default="NIE")

    ratio_1 = models.FloatField(default=2)
    ratio_2 = models.FloatField(default=2)

    deadline = models.DateTimeField(null=True)
    created_at = models.DateField(auto_now=True)

    @property
    def is_open(self) -> bool:
        return self.deadline > timezone.now()

    def voted_yes(self, amount):
        """vote impact is calcualted by this equation y=x^0.7"""
        vote_impact = (amount / self.total * 100) ** 0.7 / 100
        self.yes_ratio = round(self.yes_ratio * (1 - vote_impact), 2)
        if self.yes_ratio < 1.05:
            self.yes_ratio = 1.05
        self.no_ratio = round(self.no_ratio * (1 + vote_impact), 2)
        self.total += amount
        self.save()

    def voted_no(self, amount):
        vote_impact = (amount / self.total * 100) ** 0.7 / 100
        self.no_ratio = round(self.no_ratio * (1 - vote_impact), 2)
        if self.no_ratio < 1.05:
            self.no_ratio = 1.05
        self.yes_ratio = round(self.yes_ratio * (1 + vote_impact), 2)
        self.total += amount
        self.save()

    @property
    def total_votes(self):
        return self.votes.count()

    @property
    def yes_votes(self):
        return self.votes.filter(vote="yes").count()

    @property
    def no_votes(self):
        return self.votes.filter(vote="no").count()


class Vote(models.Model):
    class Fields(models.TextChoices):
        a = "a"
        b = "b"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes")
    bet = models.ForeignKey(Bet, on_delete=models.CASCADE, related_name="votes")
    vote = models.CharField(max_length=1)

    amount = models.IntegerField(validators=[MinValueValidator(1)])
    reward = models.IntegerField(default=0)
    has_won = models.BooleanField(default=False)
