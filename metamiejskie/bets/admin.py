from django.contrib import admin
from django import forms
from django.contrib import admin, messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import re_path
from metamiejskie.bets.models import Bet, Vote


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ["user", "bet", "vote", "amount"]


class BetCompletionForm(forms.Form):
    yes = forms.BooleanField(required=False, help_text="first value")
    no = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        track = cleaned_data.get("yes")
        session = cleaned_data.get("no")

        if track and session:
            self.add_error("yes", forms.ValidationError("Tak lub nie"))
        if not track and not session:
            self.add_error("yes", forms.ValidationError("Wybierz"))
        return cleaned_data


@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_filter = ["open"]
    list_display = ["text", "yes_ratio", "no_ratio", "total", "total_votes", "open"]
    actions = ["bet_completion"]

    def bet_completion(self, request, queryset=None):
        if "send" in request.POST:
            form = BetCompletionForm(request.POST)
            if form.is_valid():
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

            else:
                self.message_user(
                    request,
                    "Choose correct",
                    level=messages.ERROR,
                )
            path = request.get_full_path()
            path = path.rsplit("/", 2)[0] + "/"
            return HttpResponseRedirect(path)
        form = BetCompletionForm()
        form.fields["yes"].help_text = queryset[0].yes_label
        form.fields["no"].help_text = queryset[0].no_label

        return render(
            request,
            "admin/bet_completion.html",
            context={
                "form": form,
                "path": "bet_completion/",
                "queryset": queryset,
            },
        )

    bet_completion.short_description = "Close bet and payout"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [re_path("bet_completion/", self.bet_completion)]
        return custom_urls + urls
