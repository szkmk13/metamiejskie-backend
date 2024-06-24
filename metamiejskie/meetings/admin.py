from django.contrib import admin

from metamiejskie.meetings.models import Meeting, Attendance


# Register your models here.


class AttendanceInline(admin.TabularInline):
    model = Attendance


class MeetingAdmin(admin.ModelAdmin):
    list_display = ("__str__", "date")

    inlines = [AttendanceInline]


class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("user", "meeting", "confirmed")
    list_filter = ("user",)


admin.site.register(Attendance, AttendanceAdmin)
admin.site.register(Meeting, MeetingAdmin)
