from django.contrib import admin
from django import forms
from django.contrib import admin, messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import re_path

from metamiejskie.bets.forms import BetCompletionForm
from metamiejskie.bets.models import Bet, Vote
from metamiejskie.utils import DetailException


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ["user", "bet", "vote", "amount"]


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ["text", "label_1", "label_2", "ratio_1", "ratio_2", "deadline"]
    actions = ["bet_completion"]

    def calculate(self, request, queryset=None, *args, **kwargs):
        form = BetCompletionForm(request.POST)
        if not form.is_valid():
            self.message_user(
                request,
                "Choose correct",
                level=messages.ERROR,
            )
            return HttpResponseRedirect("/admin/bets/bet")
        bet = Bet.objects.get(id=form.data["bet_id"])

        print(bet)

        path = request.get_full_path()
        return HttpResponseRedirect(path)

    @admin.action(description="Close bet and payout")
    def bet_completion(self, request, queryset):
        if queryset.count() != 1:
            self.message_user(request, "Select 1 bet", level=messages.ERROR)
            return
        bet = queryset.first()
        if bet.is_open:
            self.message_user(request, "Bet is still going, come back later", level=messages.ERROR)
            return

        form = BetCompletionForm()
        form.fields["a"].help_text = bet.label_1
        form.fields["b"].help_text = bet.label_2

        return render(
            request,
            "admin/bet_completion.html",
            context={
                "form": form,
                "path": "calculate/",
                "bet": bet,
            },
        )
        if "send" in request.POST:
            form = BetCompletionForm(request.POST)
            if not form.is_valid():
                self.message_user(
                    request,
                    "Choose correct",
                    level=messages.ERROR,
                )
                path = request.get_full_path()
                path = path.rsplit("/", 2)[0] + "/"
                return HttpResponseRedirect(path)
            for bet in form.data["bets"]:
                bet = Bet.objects.get(id=bet)
                if bet.open is False:
                    self.message_user(
                        request,
                        "Bet skipped",
                    )
                    continue

                total = 0
                if form.data.get("yes"):
                    """give payout to players when answer was YES"""
                    winning_votes = Vote.objects.filter(bet=bet).filter(vote="yes")
                    losing_votes = Vote.objects.filter(bet=bet).filter(vote="no")
                    for vote in winning_votes:
                        total += vote.amount
                        vote.user.kosa_coins += vote.amount * bet.yes_ratio
                        vote.user.save()
                        vote.did_win = True
                        vote.save()
                    pass
                elif form.data.get("no"):
                    """give payout to players when answer was NO"""
                    winning_votes = Vote.objects.filter(bet=bet).filter(vote="no")
                    losing_votes = Vote.objects.filter(bet=bet).filter(vote="yes")
                    for vote in winning_votes:
                        total += vote.amount
                        vote.user.kosa_coins += vote.amount * bet.yes_ratio
                        vote.user.save()
                        vote.did_win = True
                        vote.save()
                    pass
                bet.open = False
                bet.save()
                self.message_user(
                    request,
                    f"payout given",
                )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [re_path("calculate/", self.calculate)]
        return custom_urls + urls
