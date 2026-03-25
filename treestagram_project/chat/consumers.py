import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from chat.models import ChatMessage
from posts.models import TreeFollow
from trees.models import Tree

User = get_user_model()


class TreeChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.tree_id = self.scope["url_route"]["kwargs"]["tree_id"]
        self.room_group_name = f"chat_{self.tree_id}"

        user = self.scope["user"]

        # Gate: only fans (followers) of this tree can join the group chat
        if user.is_anonymous or not await self.is_following(user.id, self.tree_id):
            await self.accept()
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "access_denied",
                        "message": "You must follow this tree to join the group chat! 🌿",
                        "user": "System",
                        "timestamp": "",
                    }
                )
            )
            await self.close()
            return

        # Join the tree's group chat
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Retrieve the last 50 messages from the database to populate history
        messages = await self.get_latest_messages(self.tree_id)
        for msg in messages:
            await self.send(
                text_data=json.dumps(
                    {
                        "type": "chat_message",
                        "message": msg["content"],
                        "user": msg["user__username"],
                        "timestamp": msg["timestamp"].isoformat(),
                    }
                )
            )

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket (frontend -> backend)
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        user = self.scope["user"]
        if user.is_anonymous:
            user_id = None
            username = "Anonymous Observer"
        else:
            user_id = user.id
            username = user.username

        # Save message to database if user is authenticated
        saved_timestamp = ""
        if user_id:
            saved_msg = await self.save_message(user_id, self.tree_id, message)
            saved_timestamp = saved_msg.timestamp.isoformat()

        # Broadcast the message to all clients in the tree's room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "user": username,
                "timestamp": saved_timestamp,
            },
        )

    async def chat_message(self, event):
        message = event["message"]
        user = event["user"]
        timestamp = event.get("timestamp", "")

        await self.send(
            text_data=json.dumps(
                {"message": message, "user": user, "timestamp": timestamp}
            )
        )

    @database_sync_to_async
    def save_message(self, user_id, tree_id, message):
        user = User.objects.get(id=user_id)
        tree = Tree.objects.get(tree_id=tree_id)
        return ChatMessage.objects.create(user=user, tree=tree, content=message)

    @database_sync_to_async
    def get_latest_messages(self, tree_id):
        messages = ChatMessage.objects.filter(tree__tree_id=tree_id).order_by(
            "-timestamp"
        )[:50]
        return list(messages.values("content", "user__username", "timestamp"))[::-1]

    @database_sync_to_async
    def is_following(self, user_id, tree_id):
        return TreeFollow.objects.filter(
            user_id=user_id, tree__tree_id=tree_id
        ).exists()
