from django.db import models
from accounts.models import User
# Create your models here.
# ---------------- Caretaker application model -------------------------
class CaretakerApplication(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="caretaker_application"
    )
    motivation = models.TextField()  # "Why do you want to be a caretaker?"
    experience = models.TextField(blank=True)  # optional experience field
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_applications"
    )

    def __str__(self):
        return f"{self.user.username} - {self.status}"
