from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model for Treestagram.
    Extends Django's AbstractUser with extra fields.
    """

    ROLE_CHOICES = [
        ("standard", "Standard User"),
        ("credible", "Credible User"),
        ("caretaker", "Caretaker"),
        ("admin", "Admin"),
    ]

    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(
        upload_to="profile_pics/", blank=True, null=True
    )
    borough = models.CharField(max_length=50, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="standard")
    post_count = models.PositiveIntegerField(default=0)
    total_likes_received = models.PositiveIntegerField(default=0)
    followed_trees_count = models.PositiveIntegerField(default=0)
    leaves = models.IntegerField(default=0)  # "credits" / karma system
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    @property
    def is_credible(self):
        return self.post_count >= 2 and self.total_likes_received >= 2

    def promote_if_eligible(self):
        """Promote standard user to credible if eligible."""
        if self.role == "standard" and self.is_credible:
            self.role = "credible"
            self.save(update_fields=["role"])

    def demote_if_ineligible(self):
        """Demote credible user back to standard if they no longer qualify."""
        if self.role == "credible" and not self.is_credible:
            self.role = "standard"
            self.save(update_fields=["role"])

    def sync_role(self):
        """Call after any post_count / total_likes_received change.
        Admins and caretakers are never touched."""
        if self.role in ("admin", "caretaker"):
            return
        if self.is_credible:
            self.promote_if_eligible()
        else:
            self.demote_if_ineligible()