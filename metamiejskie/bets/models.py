from django.db import models

from metamiejskie.users.models import User


# Create your models here.
class Bet(models.Model):
    started_by = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(default="bet")
    total = models.IntegerField(default=100)

    yes_label = models.CharField(max_length=50, default="yes")
    no_label = models.CharField(max_length=50, default="no")

    yes_ratio = models.FloatField(default=2)
    no_ratio = models.FloatField(default=2)

    open = models.BooleanField(default=True)
    deadline = models.DateTimeField(null=True)
    created_at = models.DateField(auto_now=True)

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
        return Vote.objects.filter(bet=self).count

    @property
    def yes_votes(self):
        return Vote.objects.filter(bet=self).filter(vote="yes").count()

    @property
    def no_votes(self):
        return Vote.objects.filter(bet=self).filter(vote="no").count()


class Vote(models.Model):
    VOTES = (("yes", "yes"), ("no", "no"))
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bet = models.ForeignKey(Bet, on_delete=models.CASCADE)
    vote = models.CharField(max_length=3, choices=VOTES, null=True)
    amount = models.IntegerField()
    did_win = models.BooleanField(default=False)
