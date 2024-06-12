from django.contrib import admin
from django.http import HttpResponseRedirect

from metamiejskie.casino.models import Spin, Game, Symbol


# Register your models here.


@admin.register(Symbol)
class SymbolAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "image", "weight", "value")


@admin.register(Spin)
class SpinAdmin(admin.ModelAdmin):
    list_display = ("user", "game", "amount")


class SpinInline(admin.TabularInline):
    model = Spin
    extra = 0


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("name", "spins", "id")
    actions = ["run"]
    # ordering = ['spins']
    inlines = [SpinInline]

    @admin.action()
    def run(self, request, queryset):
        obj = queryset.first()
        obj.run(user=request.user, chosen_lines=1)
        return HttpResponseRedirect("/admin/casino/game")
