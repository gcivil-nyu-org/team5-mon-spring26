from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL


class ChatMessage(models.Model):
    """Real-time chat message sent to a specific tree's group chat."""

    tree = models.ForeignKey(
        "trees.Tree", on_delete=models.CASCADE, related_name="chat_messages"
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chat_messages"
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["timestamp"]
        # Point to the EXISTING table so no data migration is needed
        db_table = "posts_chatmessage"

    def __str__(self):
        return f"[{self.tree.spc_common}] {self.user.username}: {self.content[:30]}"
