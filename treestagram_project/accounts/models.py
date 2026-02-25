from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model for Treestagram.
    Extends Django's AbstractUser with extra fields.
    """
    ROLE_CHOICES = [
        ('standard', 'Standard User'),
        ('credible', 'Credible User'),
        ('caretaker', 'Caretaker'),
        ('admin', 'Admin'),
    ]

    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(
        upload_to='profile_pics/', blank=True, null=True
    )
    borough = models.CharField(max_length=50, blank=True)
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default='standard'
    )
    post_count = models.PositiveIntegerField(default=0)
    total_likes_received = models.PositiveIntegerField(default=0)
    leaves = models.IntegerField(default=0)  # "credits" / karma system
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    @property
    def is_credible(self):
        return (
            self.post_count >= 30
            and self.total_likes_received >= 100
        )

    def promote_if_eligible(self):
        """Promote standard user to credible if eligible."""
        if self.role == 'standard' and self.is_credible:
            self.role = 'credible'
            self.save(update_fields=['role'])
