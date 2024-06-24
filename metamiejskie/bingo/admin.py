from django.contrib import admin

from metamiejskie.bingo.models import BingoField, Bingo, BingoEntry


@admin.register(Bingo)
class BingoAdmin(admin.ModelAdmin):
    list_display = ("date", "card")
    list_filter = ("date",)


@admin.register(BingoField)
class BingoFieldAdmin(admin.ModelAdmin):
    list_display = ("name",)


@admin.register(BingoEntry)
class BingoEntryAdmin(admin.ModelAdmin):
    list_display = ("date", "bingo", "marked")
    list_filter = ("date", "bingo")
