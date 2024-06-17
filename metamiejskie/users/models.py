import math

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """
    Default custom user model for metamiejskie.
    If adding fields that need to be filled at user signup,
    check forms.SignupForm and forms.SocialSignupForms accordingly.
    """

    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)

    points = models.IntegerField(default=0)
    coins = models.IntegerField(default=500)
    exp = models.IntegerField(default=0)
    level = models.IntegerField(default=1)

    @property
    def exp_to_next_level(self) -> int:
        return round(math.sqrt(self.level / 10) * 1000 + (self.level - 1) ** 2)

    def save(self, *args, **kwargs):
        if self.exp >= self.exp_to_next_level:
            self.exp -= self.exp_to_next_level
            self.level += 1
        super().save(*args, **kwargs)

    def has_daily_quest(self) -> bool:
        return self.daily_quests.filter(created_at__date=timezone.now()).exists()

    def tokens_redeemed(self) -> bool:
        if quest := self.daily_quests.filter(created_at__date=timezone.now()).first():
            return quest.redeemed
        return False

    def redeem_from_quest(self, daily_quest) -> None:
        self.coins += 100
        self.points += 10
        self.exp += daily_quest.quest.duration.total_seconds() * (daily_quest.quest.level_required + 1)
        self.save(update_fields=["coins", "points", "exp"])
        daily_quest.redeemed = True
        daily_quest.save(update_fields=["redeemed"])

    @property
    def daily_coins_redeemed(self) -> bool:
        return self.daily_coins.filter(date=timezone.now()).exists()


class DailyCoins(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="daily_coins")
    date = models.DateField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.id is None:
            self.user.coins += 10
            self.user.save(update_fields=["coins"])
        return super().save(*args, **kwargs)


class Quest(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    duration = models.DurationField(default=0, help_text="in seconds")
    level_required = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.duration.total_seconds() / 60} min {self.title}"


class DailyQuest(models.Model):
    created_at = models.DateTimeField(blank=False, default=timezone.now)
    will_end_at = models.DateTimeField(blank=True)  # editable=False
    redeemed = models.BooleanField(default=False)
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name="daily_quests")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="daily_quests")

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, *args, **kwargs):
        if self.id is None:
            self.will_end_at = self.created_at + self.quest.duration
        super().save(force_insert, force_update, using, update_fields)
