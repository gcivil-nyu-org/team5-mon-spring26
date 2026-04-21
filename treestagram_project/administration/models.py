from django.db import models
from accounts.models import User


class TreeChangeRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("dismissed", "Dismissed"),
    ]

    submitted_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="tree_change_requests"
    )
    tree_id = models.CharField(max_length=50)

    # Requested changes (all optional — only filled if caretaker wants to change)
    curb_loc = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=50, blank=True)
    health = models.CharField(max_length=50, blank=True)
    sidewalk = models.CharField(max_length=50, blank=True)
    root_stone = models.CharField(max_length=10, blank=True)   # "true"/"false"/""
    root_grate = models.CharField(max_length=10, blank=True)
    root_other = models.CharField(max_length=10, blank=True)
    trunk_wire = models.CharField(max_length=10, blank=True)
    trnk_light = models.CharField(max_length=10, blank=True)
    trnk_other = models.CharField(max_length=10, blank=True)
    brch_light = models.CharField(max_length=10, blank=True)
    brch_shoe = models.CharField(max_length=10, blank=True)
    brch_other = models.CharField(max_length=10, blank=True)
    tree_dbh = models.CharField(max_length=20, blank=True)
    stump_diam = models.CharField(max_length=20, blank=True)
    problems = models.TextField(blank=True)   # comma-joined list

    notes = models.TextField(blank=True)      # caretaker's explanation

    status_field = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending", db_column="request_status"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    dismissed_at = models.DateTimeField(null=True, blank=True)
    dismissed_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="dismissed_requests"
    )

    def __str__(self):
        return f"{self.submitted_by.username} → Tree {self.tree_id} ({self.status_field})"