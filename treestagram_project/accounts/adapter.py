import os
from allauth.account.adapter import DefaultAccountAdapter
class TreestagramAccountAdapter(DefaultAccountAdapter):
    def confirm_email(self, request, email_address):
        super().confirm_email(request, email_address)
        user = email_address.user
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=['is_active'])
    def get_email_confirmation_redirect_url(self, request):
        base_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
        return f'{base_url}/login?confirmed=true'   