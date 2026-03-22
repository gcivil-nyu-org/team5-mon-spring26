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
    leaves = models.IntegerField(default=0)  # "credits" / karma system
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    @property
    def is_credible(self):
        return self.post_count >= 30 and self.total_likes_received >= 100

    def promote_if_eligible(self):
        """Promote standard user to credible if eligible."""
        if self.role == "standard" and self.is_credible:
            self.role = "credible"
            self.save(update_fields=["role"])


class Post(models.Model):
    """A tree observation / post in the feed."""

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    tree_name = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    health = models.CharField(
        max_length=10,
        choices=[("Good", "Good"), ("Fair", "Fair"), ("Poor", "Poor")],
        default="Good",
    )
    borough = models.CharField(max_length=50, blank=True)
    image = models.ImageField(upload_to="post_images/", blank=True, null=True)
    tagged_users = models.ManyToManyField(
        User,
        blank=True,
        related_name="tagged_posts",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.tree_name} by {self.author.username}"


class Like(models.Model):
    """A like on a post (unique per user+post)."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="likes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "post")

    def __str__(self):
        return f"{self.user.username} ❤️ {self.post.tree_name}"


class Comment(models.Model):
    """A comment on a post."""

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.author.username}: {self.text[:40]}"


class Notification(models.Model):
    """
    In-app notification delivered to a user when something happens
    (like, comment, tag, role promotion, etc.).
    """

    NOTIF_TYPES = [
        ("like", "Like"),
        ("comment", "Comment"),
        ("tag", "Tagged in post"),
        ("promotion", "Role promotion"),
    ]

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_notifications",
        null=True,
        blank=True,  # null for system-generated (e.g. promotion)
    )
    notif_type = models.CharField(max_length=20, choices=NOTIF_TYPES)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
    )
    message = models.CharField(max_length=300)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.notif_type}] → {self.recipient.username}: {self.message[:50]}"
