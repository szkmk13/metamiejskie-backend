import datetime

from django.db import models
from django.db.models import Model, DateTimeField, Sum
from django.utils import timezone

from metamiejskie.users.models import User


class Place(models.Model):
    name = models.CharField(max_length=100)

    @property
    def used_in_meetings(self) -> int:
        return self.meeting_set.count()

    def __str__(self):
        return self.name


class Meeting(models.Model):
    MIN_ATTENDANCE = 3

    date = models.DateField()
    users = models.ManyToManyField(User, through="Attendance")
    place = models.ForeignKey(Place, on_delete=models.SET_NULL, null=True)

    pizza = models.BooleanField(default=False)
    casino = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.date} {self.place.name}"

    @property
    def is_confirmed_by_users(self) -> bool:
        attendances = self.attendance_set.all()
        confirmed_count = attendances.filter(confirmed=True).count()
        if confirmed_count > 1:
            return True
        return False

    @staticmethod
    def count_attendance(user) -> int:
        return Attendance.objects.filter(user=user).count()

    @property
    def how_many_attended(self) -> int:
        return self.users.count()

    @property
    def confirmed_by_less_than_2_users(self) -> bool:
        confirmed_count = self.attendance_set.filter(confirmed=True).count()
        return confirmed_count < 2

    def confirmed_by_user(self, user):
        if user in self.users.all():
            return self.attendance_set.get(user=user).confirmed
        return False


class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="+")
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE)
    drinking = models.BooleanField(default=True)
    confirmed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} at {self.meeting}"
