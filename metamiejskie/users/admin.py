# from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _

from .forms import UserAdminChangeForm
from .forms import UserAdminCreationForm
from .models import User, Quest, DailyQuest, DailyCoins

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    # Force the `admin` sign in process to go through the `django-allauth` workflow:
    # https://docs.allauth.org/en/latest/common/admin.html#admin
    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)  # type: ignore[method-assign]


@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = ("title", "description", "duration", "level_required")


@admin.register(DailyCoins)
class DailyCoinsAdmin(admin.ModelAdmin):
    list_display = ("date", "user")
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
