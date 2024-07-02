from django.contrib import admin
from django.http import HttpResponseRedirect

from metamiejskie.casino.models import Spin, Game, Symbol, HighCard


@admin.register(HighCard)
class CardGameAdmin(admin.ModelAdmin):
    list_display = ("user",)
    actions = ["play"]

    @admin.action()
    def play(self, request, queryset):
        obj = queryset.first()
        obj.play()
        return HttpResponseRedirect("/admin/casino/cardgame")


@admin.register(Symbol)
class SymbolAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "image", "weight", "value")


@admin.register(Spin)
class SpinAdmin(admin.ModelAdmin):
    list_display = ("user", "game", "amount")


class SpinInline(admin.TabularInline):
    model = Spin
    extra = 0


#
# @admin.register(Game)
# class GameAdmin(admin.ModelAdmin):
#     list_display = ("name", "spins", "id")
#     actions = ["play"]
#     # ordering = ['spins']
#     inlines = [SpinInline]
#
#     @admin.action()
#     def run(self, request, queryset):
#         obj = queryset.first()
#         obj.play(user=request.user, chosen_lines=1)
#         return HttpResponseRedirect("/admin/casino/game")
