import os
from allauth.account.adapter import DefaultAccountAdapter


class TreestagramAccountAdapter(DefaultAccountAdapter):
    def get_email_verification_redirect_url(self, email_address):
        base_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
        return f"{base_url}/login?confirmed=true"