from allauth.account.signals import email_confirmed
from django.dispatch import receiver


@receiver(email_confirmed)
def activate_user_on_confirm(sender, request, email_address, **kwargs):
    """When a user confirms their email, activate their account."""
    user = email_address.user
    if not user.is_active:
        user.is_active = True
        user.save(update_fields=["is_active"])
