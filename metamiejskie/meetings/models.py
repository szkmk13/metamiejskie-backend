import datetime

from django.db import models
from django.db.models import Model, DateTimeField
from django.utils import timezone

from metamiejskie.users.models import User


class Meeting(models.Model):
    def save(self, *args, **kwargs):
        if self.place != "OTHER":
            self.other_place = None
        super(Meeting, self).save(*args, **kwargs)

    MIN_ATTENDANCE = 3
    date = models.DateField()
    participants = models.ManyToManyField(User, through="Attendance")
    place = models.CharField(max_length=30)
    other_place = models.CharField(max_length=30, blank=True, null=True)
    pizza = models.BooleanField(default=False)
    kasyno = models.BooleanField(default=False)

    # who_paid = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    def __str__(self):
        names = [user.get_full_name() for user in self.participants.all()]
        return f"{self.other_place} of {names}" if self.other_place else f"Meeting at {self.place} of {names}"

    def is_confirmed_by_users(self):
        attendances = self.attendance_set.all()
        confirmed_count = attendances.filter(confirmed=True).count()
        if confirmed_count > 1:
            return True
        return False

    @staticmethod
    def count_attendance(user):
        return Attendance.objects.filter(user=user)

    @property
    def how_many_attended(self):
        return self.participants.count()

    @property
    def confirmed_by_less_than_2_users(self):
        confirmed = 0
        attendances = self.attendance_set.all()
        for _ in attendances:
            if _.confirmed:
                confirmed += 1
        return confirmed < 2

    def confirmed_by_user(self, user):
        if user in self.participants.all():
            return self.attendance_set.get(user=user).confirmed
        return False


class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    drinking = models.BooleanField(default=True)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} at {self.meeting}"
