from django.contrib import admin
from django import forms
from django.contrib import admin, messages
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import re_path
from metamiejskie.bets.models import Bet, Vote
from metamiejskie.utils import DetailException



class BetCompletionForm(forms.Form):
    a = forms.BooleanField(required=False)
    b = forms.BooleanField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        track = cleaned_data.get("a")
        session = cleaned_data.get("b")

        if track and session:
            self.add_error("a", DetailException("Tak lub nie"))
        if not track and not session:
            self.add_error("a", DetailException("Wybierz"))
        return cleaned_data
