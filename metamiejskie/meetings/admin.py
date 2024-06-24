from django.contrib import admin

from metamiejskie.meetings.models import Meeting, Attendance, Place


# Register your models here.


class AttendanceInline(admin.TabularInline):
    model = Attendance


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ("__str__", "date")

    inlines = [AttendanceInline]


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("user", "meeting", "confirmed")
    list_filter = ("user",)


@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    list_display = ("name",)
