from allauth.account.adapter import DefaultAccountAdapter


class TreestagramAccountAdapter(DefaultAccountAdapter):
    def confirm_email(self, request, email_address):
        """Activate the user when their email is confirmed."""
        super().confirm_email(request, email_address)
        user = email_address.user
        if not user.is_active:
            user.is_active = True
            user.save(update_fields=['is_active'])

    def get_email_confirmation_redirect_url(self, request):
        """Redirect to the Svelte frontend login page after confirmation."""
        return 'http://localhost:5173/login?confirmed=true'
