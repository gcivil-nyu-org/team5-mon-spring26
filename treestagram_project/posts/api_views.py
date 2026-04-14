import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from accounts.models import User
from accounts.api_views import user_to_dict
from trees.models import Tree
from caretaker.models import CaretakerAssignment
from .models import Post, Like, Comment, Notification, TreeFollow
from chat.models import ChatMessage

# ── Post / Like / Comment endpoints ─────────────────────────────────────────


def _post_to_dict(post, request_user):
    """Serialize a Post to a JSON-safe dict."""
    liked = False
    if request_user.is_authenticated:
        liked = post.likes.filter(user=request_user).exists()
    return {
        "id": post.id,
        "tree_id": post.tree.tree_id if post.tree else None,
        "tree_name": post.tree_name,
        "body": post.body,
        "health": post.health,
        "borough": post.borough,
        "image": post.image.url if post.image else None,
        "author": {
            "id": post.author_id,
            "username": post.author.username,
            "profile_picture": (
                post.author.profile_picture.url if post.author.profile_picture else None
            ),
        },
        "tagged_users": [
            {"id": u.id, "username": u.username} for u in post.tagged_users.all()
        ],
        "likes_count": post.likes.count(),
        "liked": liked,
        "comments": [
            {
                "id": c.id,
                "text": c.text,
                "author": {
                    "id": c.author_id,
                    "username": c.author.username,
                },
                "created_at": c.created_at.isoformat(),
            }
            for c in post.comments.select_related("author").all()
        ],
        "created_at": post.created_at.isoformat(),
        "following": (
            TreeFollow.objects.filter(user=request_user, tree=post.tree).exists()
            if request_user.is_authenticated and post.tree
            else False
        ),
    }


def api_fetch_posts(request):
    """GET /api/posts/ — followed-tree posts first, then same-borough posts (no duplicates)."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": True, "posts": []})

    # Tree PKs the user follows
    followed_tree_pks = set(
        TreeFollow.objects.filter(user=request.user).values_list("tree_id", flat=True)
    )

    prefetch_fields = ("likes", "comments__author", "tagged_users")

    # 1) Posts from followed trees (newest first)
    followed_posts = list(
        Post.objects.filter(tree_id__in=followed_tree_pks)
        .select_related("author", "tree")
        .prefetch_related(*prefetch_fields)
    )

    # 2) Posts from the user's borough, excluding already-followed trees
    borough_posts = []
    user_borough = (request.user.borough or "").strip()
    if user_borough:
        borough_posts = list(
            Post.objects.filter(borough__iexact=user_borough)
            .exclude(tree_id__in=followed_tree_pks)
            .select_related("author", "tree")
            .prefetch_related(*prefetch_fields)
        )

    all_posts = followed_posts + borough_posts

    return JsonResponse(
        {
            "success": True,
            "posts": [_post_to_dict(p, request.user) for p in all_posts],
        }
    )


def api_fetch_my_posts(request):
    """GET /api/my-posts/ — return posts authored by the current user."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)
    posts = (
        Post.objects.filter(author=request.user)
        .select_related("author")
        .prefetch_related(
            "likes",
            "comments__author",
            "tagged_users",
        )
    )
    return JsonResponse(
        {
            "success": True,
            "posts": [_post_to_dict(p, request.user) for p in posts],
        }
    )


def api_fetch_my_tagged_posts(request):
    """GET /api/my-tagged-posts/ — return posts where the current user is tagged."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)
    posts = request.user.tagged_posts.select_related("author").prefetch_related(
        "likes",
        "comments__author",
        "tagged_users",
    )
    return JsonResponse(
        {
            "success": True,
            "posts": [_post_to_dict(p, request.user) for p in posts],
        }
    )


@require_http_methods(["GET"])
def api_fetch_tree_posts(request, tree_id):
    """GET /api/trees/<tree_id>/posts/ — return posts for a specific tree."""
    posts = (
        Post.objects.filter(tree__tree_id=tree_id)
        .select_related("author", "tree")
        .prefetch_related(
            "likes",
            "comments__author",
            "tagged_users",
        )
    )
    return JsonResponse(
        {
            "success": True,
            "posts": [_post_to_dict(p, request.user) for p in posts],
        }
    )


@require_http_methods(["GET"])
def api_validate_tree(request):
    """GET /api/validate-tree/?tree_id=12345 — check if a tree_id exists."""
    tree_id = request.GET.get("tree_id", "").strip()
    if not tree_id:
        return JsonResponse({"exists": False, "error": "tree_id is required"})
    try:
        tree = Tree.objects.get(tree_id=int(tree_id))
        return JsonResponse(
            {
                "exists": True,
                "tree": {
                    "tree_id": tree.tree_id,
                    "spc_common": tree.spc_common,
                    "spc_latin": tree.spc_latin,
                    "borough": tree.borough,
                    "health": tree.health,
                    "address": tree.address,
                },
            }
        )
    except (Tree.DoesNotExist, ValueError):
        return JsonResponse({"exists": False, "error": "Tree ID not found in database"})


@require_http_methods(["POST"])
def api_create_post(request):
    """POST /api/posts/create/ — create a new post (multipart or JSON)."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    if request.content_type and "multipart" in request.content_type:
        data = request.POST
        image = request.FILES.get("image")
    else:
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
        image = None

    # ── Validate tree_id ──
    tree_id_str = data.get("tree_id", "").strip()
    if not tree_id_str:
        return JsonResponse(
            {"success": False, "error": "tree_id is required"}, status=400
        )

    try:
        tree = Tree.objects.get(tree_id=int(tree_id_str))
    except (Tree.DoesNotExist, ValueError):
        return JsonResponse(
            {
                "success": False,
                "error": f'Tree ID "{tree_id_str}" not found in database',
            },
            status=400,
        )

    # Auto-fill tree_name from the matched tree
    tree_name = tree.spc_common or f"Tree #{tree.tree_id}"

    post = Post.objects.create(
        author=request.user,
        tree=tree,
        tree_name=tree_name,
        body=data.get("body", ""),
        health=data.get("health", "Good"),
        borough=tree.borough or data.get("borough", ""),
        image=image if image else None,
    )

    # Handle tagged users
    tagged_users_str = data.get("tagged_users", "")
    if tagged_users_str:
        usernames = [
            u.strip().lstrip("@") for u in tagged_users_str.split(",") if u.strip()
        ]
        tagged = User.objects.filter(username__in=usernames)
        post.tagged_users.set(tagged)

        # ── Notification: you were tagged in a post ──
        for tagged_user in tagged:
            _create_notification(
                recipient=tagged_user,
                sender=request.user,
                notif_type="tag",
                message=f'@{request.user.username} tagged you in a post about "{post.tree_name}"',
                post=post,
            )

    # Update post count
    request.user.post_count = Post.objects.filter(author=request.user).count()
    request.user.save(update_fields=["post_count"])

    # Check promotion (and notify if promoted)
    old_role = request.user.role
    request.user.sync_role()
    if request.user.role != old_role:
        _create_notification(
            recipient=request.user,
            sender=None,
            notif_type="promotion",
            message=f"Congrats! You've been promoted to {request.user.get_role_display()}!",
        )

    return JsonResponse(
        {
            "success": True,
            "post": _post_to_dict(post, request.user),
            "user": user_to_dict(request.user),
        }
    )


@require_http_methods(["POST"])
def api_delete_post(request, post_id):
    """POST /api/posts/<id>/delete/ — delete a post.
    Allowed by: post author, admin, or caretaker of the post's tree."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    try:
        post = Post.objects.select_related("tree").get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"success": False, "error": "Post not found"}, status=404)

    is_author = post.author_id == request.user.id
    is_admin = request.user.role == "admin"
    is_caretaker = (
        post.tree
        and CaretakerAssignment.objects.filter(
            user=request.user, tree_id=post.tree.tree_id
        ).exists()
    )

    if not (is_author or is_admin or is_caretaker):
        return JsonResponse(
            {"success": False, "error": "Permission denied"}, status=403
        )

    # Keep a reference to the original author for stat updates
    post_author = post.author
    post.delete()

    # Update the original author's post count and total likes received
    post_author.post_count = Post.objects.filter(author=post_author).count()
    post_author.total_likes_received = Like.objects.filter(
        post__author=post_author
    ).count()
    post_author.save(update_fields=["post_count", "total_likes_received"])
    post_author.sync_role()

    return JsonResponse({"success": True})


@require_http_methods(["POST"])
def api_toggle_like(request, post_id):
    """POST /api/posts/<id>/like/ — toggle like on a post."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"success": False, "error": "Post not found"}, status=404)

    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if not created:
        like.delete()

    likes_count = post.likes.count()

    # Update author's total_likes_received
    post.author.total_likes_received = Like.objects.filter(
        post__author=post.author
    ).count()
    post.author.save(update_fields=["total_likes_received"])

    # ── Notification: someone liked your post ──
    if created:
        _create_notification(
            recipient=post.author,
            sender=request.user,
            notif_type="like",
            message=f'@{request.user.username} liked your post "{post.tree_name}"',
            post=post,
        )

    # Check promotion (and notify if promoted)
    old_role = post.author.role
    post.author.sync_role()
    if post.author.role != old_role:
        _create_notification(
            recipient=post.author,
            sender=None,
            notif_type="promotion",
            message=f"Congrats! You've been promoted to {post.author.get_role_display()}!",
        )

    return JsonResponse(
        {
            "success": True,
            "liked": created,
            "likes_count": likes_count,
        }
    )


@require_http_methods(["POST"])
def api_add_comment(request, post_id):
    """POST /api/posts/<id>/comment/ — add a comment to a post."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    text = data.get("text", "").strip()
    if not text:
        return JsonResponse(
            {"success": False, "error": "Comment text is required"}, status=400
        )

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"success": False, "error": "Post not found"}, status=404)

    comment = Comment.objects.create(author=request.user, post=post, text=text)

    # ── Notification: someone commented on your post ──
    _create_notification(
        recipient=post.author,
        sender=request.user,
        notif_type="comment",
        message=f'@{request.user.username} commented on your post "{post.tree_name}"',
        post=post,
        comment=comment,
    )

    return JsonResponse(
        {
            "success": True,
            "comment": {
                "id": comment.id,
                "text": comment.text,
                "author": {
                    "id": comment.author_id,
                    "username": comment.author.username,
                },
                "created_at": comment.created_at.isoformat(),
            },
        }
    )


@require_http_methods(["POST"])
def api_edit_comment(request, comment_id):
    """POST /api/comments/<id>/edit/ — edit a comment (author only)."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    try:
        comment = Comment.objects.select_related("author").get(id=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Comment not found"}, status=404
        )

    if comment.author_id != request.user.id:
        return JsonResponse(
            {"success": False, "error": "You can only edit your own comments"},
            status=403,
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    text = data.get("text", "").strip()
    if not text:
        return JsonResponse(
            {"success": False, "error": "Comment text is required"}, status=400
        )

    comment.text = text
    comment.save(update_fields=["text"])

    return JsonResponse(
        {
            "success": True,
            "comment": {
                "id": comment.id,
                "text": comment.text,
                "author": {
                    "id": comment.author_id,
                    "username": comment.author.username,
                },
                "created_at": comment.created_at.isoformat(),
            },
        }
    )


@require_http_methods(["POST"])
def api_delete_comment(request, comment_id):
    """POST /api/comments/<id>/delete/ — delete a comment.
    Allowed by: comment author, post author, admin, or caretaker of the post's tree."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    try:
        comment = Comment.objects.select_related("post", "post__tree").get(
            id=comment_id
        )
    except Comment.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Comment not found"}, status=404
        )

    is_comment_author = comment.author_id == request.user.id
    is_post_author = comment.post.author_id == request.user.id
    is_admin = request.user.role == "admin"
    is_caretaker = (
        comment.post.tree
        and CaretakerAssignment.objects.filter(
            user=request.user, tree_id=comment.post.tree.tree_id
        ).exists()
    )

    if not (is_comment_author or is_post_author or is_admin or is_caretaker):
        return JsonResponse(
            {"success": False, "error": "Permission denied"}, status=403
        )

    comment.delete()

    return JsonResponse({"success": True})


# ── Notification helpers ──────────────────────────────────────────────────────


def _create_notification(
    recipient, sender, notif_type, message, post=None, comment=None
):
    """Create a notification (skips if recipient == sender)."""
    if sender and recipient.id == sender.id:
        return None
    return Notification.objects.create(
        recipient=recipient,
        sender=sender,
        notif_type=notif_type,
        message=message,
        post=post,
        comment=comment,
    )


def _notif_to_dict(notif):
    """Serialize a Notification to a JSON-safe dict."""
    return {
        "id": notif.id,
        "notif_type": notif.notif_type,
        "message": notif.message,
        "is_read": notif.is_read,
        "created_at": notif.created_at.isoformat(),
        "sender": (
            {
                "id": notif.sender.id,
                "username": notif.sender.username,
                "profile_picture": (
                    notif.sender.profile_picture.url
                    if notif.sender.profile_picture
                    else None
                ),
            }
            if notif.sender
            else None
        ),
        "post_id": notif.post_id,
        "comment_id": notif.comment_id,
    }


# ── Notification API endpoints ───────────────────────────────────────────────


def api_notifications(request):
    """GET /api/notifications/ — return current user's notifications (newest first)."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    notifications = (
        Notification.objects.filter(recipient=request.user)
        .select_related("sender", "post")
        .order_by("-created_at")[:50]
    )
    unread_count = Notification.objects.filter(
        recipient=request.user, is_read=False
    ).count()

    return JsonResponse(
        {
            "success": True,
            "notifications": [_notif_to_dict(n) for n in notifications],
            "unread_count": unread_count,
        }
    )


def api_notifications_unread_count(request):
    """GET /api/notifications/unread-count/ — lightweight unread count."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    count = Notification.objects.filter(recipient=request.user, is_read=False).count()
    return JsonResponse({"success": True, "unread_count": count})


@require_http_methods(["POST"])
def api_notifications_mark_read(request):
    """POST /api/notifications/mark-read/ — mark specific notifications as read."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    notif_ids = data.get("ids", [])
    if notif_ids:
        Notification.objects.filter(recipient=request.user, id__in=notif_ids).update(
            is_read=True
        )

    return JsonResponse({"success": True})


@require_http_methods(["POST"])
def api_notifications_mark_all_read(request):
    """POST /api/notifications/mark-all-read/ — mark ALL notifications as read."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    Notification.objects.filter(recipient=request.user, is_read=False).update(
        is_read=True
    )
    return JsonResponse({"success": True})


# ── Tree Follow endpoints ────────────────────────────────────────────────────


@require_http_methods(["POST"])
def api_toggle_tree_follow(request, tree_id):
    """POST /api/trees/<tree_id>/follow/ — toggle follow/unfollow for a tree."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    try:
        tree = Tree.objects.get(tree_id=tree_id)
    except Tree.DoesNotExist:
        return JsonResponse({"success": False, "error": "Tree not found"}, status=404)

    follow, created = TreeFollow.objects.get_or_create(user=request.user, tree=tree)
    if not created:
        follow.delete()
        following = False
    else:
        following = True

        # Broadcast "user joined" to the tree's group chat
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"chat_{tree_id}",
            {
                "type": "chat_message",
                "message": f"🌱 @{request.user.username} (ID: {request.user.id}) just joined the community!",
                "user": "System",
                "timestamp": "",
            },
        )

    # Update cached counter
    request.user.followed_trees_count = TreeFollow.objects.filter(
        user=request.user
    ).count()
    request.user.save(update_fields=["followed_trees_count"])

    follower_count = TreeFollow.objects.filter(tree=tree).count()

    return JsonResponse(
        {
            "success": True,
            "following": following,
            "follower_count": follower_count,
        }
    )


@require_http_methods(["GET"])
def api_my_followed_trees(request):
    """GET /api/my-followed-trees/ — return list of tree IDs the user follows."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    follows = TreeFollow.objects.filter(user=request.user).select_related("tree")
    trees = []

    for f in follows:
        last_msg = (
            ChatMessage.objects.filter(tree=f.tree)
            .order_by("-timestamp", "-pk")
            .first()
        )
        trees.append(
            {
                "tree_id": f.tree.tree_id,
                "tree_name": f.tree.spc_common or "Unknown",
                "followed_at": f.created_at.isoformat(),
                "notify": f.notify,
                "has_messages": last_msg is not None,
                "last_message": last_msg.content if last_msg else None,
                "last_message_time": (
                    last_msg.timestamp.isoformat() if last_msg else None
                ),
            }
        )

    return JsonResponse({"success": True, "trees": trees})
