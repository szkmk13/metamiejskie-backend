# from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _

from .forms import UserAdminChangeForm
from .forms import UserAdminCreationForm
from .models import User, Quest, DailyQuest, DailyCoins, Variables


@admin.register(Variables)
class VariablesAdmin(admin.ModelAdmin):
    list_display = ("name", "value")


@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "duration", "level_required")


@admin.register(DailyCoins)
class DailyCoinsAdmin(admin.ModelAdmin):
    list_display = ("date", "user", "amount")
    list_filter = ("date", "user")


@admin.register(DailyQuest)
class DailyQuestAdmin(admin.ModelAdmin):
    list_display = ("user", "quest", "created_at", "will_end_at")


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("name", "email")}),
        # (
        #     _("Permissions"),
        #     {
        #         "fields": (
        #             "is_active",
        #             "is_staff",
        #             "is_superuser",
        #             "groups",
        #             "user_permissions",
        #         ),
        #     },
        # ),
        ("Trójmiejskie", {"fields": ("level", "exp", "coins", "points")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["username", "name", "level", "exp", "points", "coins"]
    search_fields = ["name"]
