from __future__ import annotations

import typing

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

if typing.TYPE_CHECKING:
    from allauth.socialaccount.models import SocialLogin
    from django.http import HttpRequest

    from metamiejskie.users.models import User


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request: HttpRequest) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def send_mail(self, template_prefix, email, context):
        ctx = {
            "email": email,
        }
        ctx.update(context)
        # if backend_reset_url := ctx.get("password_reset_url"):
        #     backend_reset_url = backend_reset_url.split("/")
        #     ctx['password_reset_url'] = settings.FRONTEND_URL+"/"+backend_reset_url[-2]+"/"+backend_reset_url[-1]
        msg = self.render_mail(template_prefix, email, ctx)
        msg.send()

    def get_email_confirmation_url(self, request, emailconfirmation):
        """Constructs the email confirmation (activation) url.

        Note that if you have architected your system such that email
        confirmations are sent outside of the request context `request`
        can be `None` here.
        """
        url = settings.FRONTEND_URL
        # return f'{url}/?key={emailconfirmation.key}'
        from allauth.account.internal import flows

        return flows.manage_email.get_email_verification_url(request, emailconfirmation)
    def get_reset_password_from_key_url(self, key):
        """
        Method intented to be overriden in case the password reset email
        needs to be adjusted.
        """
        url = settings.FRONTEND_URL
        # return f'{url}/?key={emailconfirmation.key}'
        from allauth.account.internal import flows
        print('UDSADSAIPASPO')
        return flows.password_reset.get_reset_password_from_key_url(self.request, key)

class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
    ) -> bool:
        return getattr(settings, "ACCOUNT_ALLOW_REGISTRATION", True)

    def populate_user(
        self,
        request: HttpRequest,
        sociallogin: SocialLogin,
        data: dict[str, typing.Any],
    ) -> User:
        """
        Populates user information from social provider info.

        See: https://docs.allauth.org/en/latest/socialaccount/advanced.html#creating-and-populating-user-instances
        """
        user = super().populate_user(request, sociallogin, data)
        if not user.name:
            if name := data.get("name"):
                user.name = name
            elif first_name := data.get("first_name"):
                user.name = first_name
                if last_name := data.get("last_name"):
                    user.name += f" {last_name}"
        return user
