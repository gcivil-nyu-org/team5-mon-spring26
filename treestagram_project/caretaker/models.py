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

    # Links to the user applying
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="caretaker_applications"
    )

    # The specific tree they are applying for
    tree_id = models.CharField(max_length=50, null=True, blank=True)

    motivation = models.TextField()
    experience = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

    # Automatically saves the date/time when created
    submitted_at = models.DateTimeField(auto_now_add=True)

    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reviewed_applications",
    )

    def __str__(self):
        return f"{self.user.username} - {self.tree_id} - {self.status}"


class CaretakerAssignment(models.Model):
    # The user who is the caretaker
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="tree_assignments"
    )

    # The tree they are assigned to
    tree_id = models.CharField(max_length=50, null=True, blank=True)

    # Helpful to know when they became the caretaker
    assigned_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} taking care of {self.tree_id}"
