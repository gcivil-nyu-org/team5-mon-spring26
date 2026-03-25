from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class Post(models.Model):
    """A tree observation / post in the feed."""

    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    tree = models.ForeignKey(
        "trees.Tree",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
    )
    tree_name = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    health = models.CharField(
        max_length=10,
        choices=[("Good", "Good"), ("Fair", "Fair"), ("Poor", "Poor")],
        default="Good",
    )
    borough = models.CharField(max_length=50, blank=True)
    image = models.TextField(blank=True, null=True)  # base64 encoded image data
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
        # We need to fetch the author username if we use settings.AUTH_USER_MODEL
        # but author is a User reference so this works.
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


class TreeFollow(models.Model):
    """A user following a specific tree to get updates."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="tree_follows"
    )
    tree = models.ForeignKey(
        "trees.Tree", on_delete=models.CASCADE, related_name="followers"
    )
    notify = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "tree")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} follows {self.tree.spc_common}"
