"""
accounts/api_views.py
JSON API endpoints consumed by the Svelte frontend.
"""

import json
import logging
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from allauth.account.models import EmailAddress
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .forms import SignupForm
from .models import User, Notification
from .models import Post, Like, Comment

logger = logging.getLogger(__name__)


def user_to_dict(user):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "borough": user.borough,
        "role": user.role,
        "bio": user.bio,
        "profile_picture": user.profile_picture.url if user.profile_picture else None,
        "post_count": user.post_count,
        "total_likes_received": user.total_likes_received,
        "leaves": user.leaves,
    }


@ensure_csrf_cookie
def csrf_view(request):
    """Hit this endpoint to get the CSRF cookie set."""
    return JsonResponse({"csrfToken": get_token(request)})


@require_http_methods(["POST"])
def api_signup(request):
    try:
        data = json.loads(request.body)
        logger.info("Received data: %s", data)
    except json.JSONDecodeError:
        logger.error("Invalid JSON")
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    form = SignupForm(data)
    if form.is_valid():
        logger.info("Form is valid")
        user = form.save(commit=False)
        user.is_active = False  # inactive until email is confirmed
        user.save()
        logger.info("User created: %s", user)

        try:
            email_address = EmailAddress.objects.create(
                user=user,
                email=user.email,
                primary=True,
                verified=False,
            )
            logger.info("EmailAddress created: %s", email_address)
            email_address.send_confirmation(request)
            logger.info("Confirmation email sent")
        except Exception:
            logger.exception("Error sending confirmation email")
            return JsonResponse(
                {"success": False, "error": "Failed to send confirmation email"},
                status=500,
            )

        return JsonResponse(
            {
                "success": True,
                "requires_verification": True,
                "message": "Account created! Check your email for a confirmation link.",
            }
        )
    else:
        logger.error("Form errors: %s", form.errors)
        return JsonResponse({"success": False, "errors": form.errors}, status=400)


@require_http_methods(["POST"])
def api_login(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    username = data.get("username", "").strip()
    password = data.get("password", "")

    if not username or not password:
        return JsonResponse(
            {"success": False, "error": "Username and password required."}, status=400
        )

    # Try authenticating by username first, then fall back to email
    user = authenticate(request, username=username, password=password)
    if user is None:
        # Try looking up by email
        try:
            user_obj = User.objects.get(email__iexact=username)
            user = authenticate(request, username=user_obj.username, password=password)
        except User.DoesNotExist:
            pass

    if user:
        # Check if user has verified their email
        if not user.is_active:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Please verify your email before logging in. Check your inbox for a confirmation link.",
                    "requires_verification": True,
                },
                status=403,
            )

        login(request, user)
        return JsonResponse({"success": True, "user": user_to_dict(user)})
    else:
        return JsonResponse(
            {"success": False, "error": "Invalid username or password."}, status=401
        )


@require_http_methods(["POST"])
def api_logout(request):
    logout(request)
    return JsonResponse({"success": True})


def api_check_username(request):
    """Check if a username is already taken."""
    username = request.GET.get("username", "").strip()
    if len(username) < 3:
        return JsonResponse({"available": False, "error": "Too short"})
    taken = User.objects.filter(username__iexact=username).exists()
    return JsonResponse({"available": not taken})


def api_me(request):
    """Return current user info if logged in."""
    if request.user.is_authenticated:
        return JsonResponse(
            {"success": True, "user": user_to_dict(request.user)}
            | user_to_dict(request.user)
        )
    return JsonResponse({"success": False}, status=401)


def api_google_login_url(request):
    """Return the Google OAuth login URL for the Svelte frontend to redirect to."""
    return JsonResponse(
        {
            "url": "/accounts/google/login/?process=login",
        }
    )


@require_http_methods(["POST"])
def api_resend_verification(request):
    """Resend verification email for a given email address."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    email = data.get("email", "").strip()
    if not email:
        return JsonResponse(
            {"success": False, "error": "Email is required."}, status=400
        )

    try:
        email_address = EmailAddress.objects.get(email__iexact=email, verified=False)
        email_address.send_confirmation(request)
        return JsonResponse({"success": True, "message": "Verification email sent!"})
    except EmailAddress.DoesNotExist:
        return JsonResponse(
            {
                "success": False,
                "error": "No unverified account found with this email.",
            },
            status=404,
        )


@require_http_methods(["POST"])
def api_forgot_password(request):
    """Send a password reset email for the given email address."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    email = data.get("email", "").strip()
    if not email:
        return JsonResponse(
            {"success": False, "error": "Email address is required."}, status=400
        )

    form = PasswordResetForm({"email": email})
    if form.is_valid():
        form.save(
            request=request,
            use_https=request.is_secure(),
            from_email=None,  # uses DEFAULT_FROM_EMAIL
            email_template_name="registration/password_reset_email.html",
            subject_template_name="registration/password_reset_subject.txt",
        )

    # Always return success to avoid leaking whether the email exists
    return JsonResponse(
        {
            "success": True,
            "message": "If an account exists with this email, a password reset link has been sent.",
        }
    )


def api_verify_reset_token(request, uidb64, token):
    """Check whether a password-reset token is still valid (GET)."""
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return JsonResponse({"valid": False})

    if default_token_generator.check_token(user, token):
        return JsonResponse({"valid": True})
    return JsonResponse({"valid": False})


@require_http_methods(["POST"])
def api_reset_password(request, uidb64, token):
    """Validate token and set the new password."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    password = data.get("password", "")
    if not password:
        return JsonResponse(
            {"success": False, "error": "Password is required."}, status=400
        )

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return JsonResponse(
            {"success": False, "error": "Invalid reset link."}, status=400
        )

    if not default_token_generator.check_token(user, token):
        return JsonResponse(
            {
                "success": False,
                "error": "This reset link has expired. Please request a new one.",
            },
            status=400,
        )

    # Validate password using Django validators
    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError

    try:
        validate_password(password, user)
    except ValidationError as e:
        return JsonResponse(
            {"success": False, "error": " ".join(e.messages)}, status=400
        )

    user.set_password(password)
    user.save()
    return JsonResponse(
        {"success": True, "message": "Password has been reset successfully."}
    )


@require_http_methods(["POST"])
def api_update_profile(request):
    """Update current user profile info and photo."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    user = request.user

    # Handle basic info (could be JSON or Form Data)
    # If Content-Type is multipart/form-data, data is in request.POST
    # If Content-Type is application/json, data is in request.body

    if request.content_type == "application/json":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    else:
        # Fallback to POST for multipart/form-data
        data = request.POST

    # Fields allowed to be updated
    allowed_fields = ["first_name", "last_name", "username", "bio", "borough"]

    for field in allowed_fields:
        if field in data:
            val = data.get(field)
            if field == "username":
                val = val.strip().lower()
                if val != user.username and User.objects.filter(username=val).exists():
                    return JsonResponse(
                        {"success": False, "error": f'Username "{val}" is taken.'},
                        status=400,
                    )
            setattr(user, field, val)

    # Handle Photo Upload or Removal
    if "profile_picture" in request.FILES:
        user.profile_picture = request.FILES["profile_picture"]
    elif data.get("remove_photo") == "true":
        user.profile_picture = None

    try:
        user.save()
        return JsonResponse(
            {
                "success": True,
                "user": user_to_dict(user),
                "message": "Profile updated successfully!",
            }
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)


@require_http_methods(["POST"])
def api_verify_password(request):
    """Real-time validation of the current password."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    password = data.get("password")
    if not password:
        return JsonResponse(
            {"success": False, "error": "Password required"}, status=400
        )

    is_correct = request.user.check_password(password)
    return JsonResponse({"success": True, "is_correct": is_correct})


@require_http_methods(["POST"])
def api_change_password(request):
    """Securely update the password for the current authenticated user."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    current_password = data.get("current_password")
    new_password = data.get("new_password")
    confirm_password = data.get("confirm_password")

    if not current_password or not new_password or not confirm_password:
        return JsonResponse(
            {"success": False, "error": "All fields are required."}, status=400
        )

    if new_password != confirm_password:
        return JsonResponse(
            {"success": False, "error": "New passwords do not match."}, status=400
        )

    user = request.user

    # Verify current password
    if not user.check_password(current_password):
        return JsonResponse(
            {"success": False, "error": "Current password incorrect."}, status=400
        )

    # Validate new password
    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError

    try:
        validate_password(new_password, user)
    except ValidationError as e:
        return JsonResponse(
            {"success": False, "error": " ".join(e.messages)}, status=400
        )

    # Set new password and keep session alive
    from django.contrib.auth import update_session_auth_hash

    user.set_password(new_password)
    user.save()
    update_session_auth_hash(request, user)

    return JsonResponse({"success": True, "message": "Password changed successfully."})


@require_http_methods(["POST"])
def api_delete_account(request):
    """
    Deletes the current user's account after password verification.
    """
    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "error": "Not authenticated."}, status=401
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    password = data.get("password")
    if not password:
        return JsonResponse(
            {"success": False, "error": "Password is required to confirm deletion."},
            status=400,
        )

    if not request.user.check_password(password):
        return JsonResponse(
            {"success": False, "error": "Incorrect password."}, status=400
        )

    user = request.user
    user_email = user.email
    first_name = user.first_name
    username = user.username

    # Send confirmation email
    subject = "Your Treestagram account has been deleted"
    html_message = render_to_string(
        "accounts/account_deleted_email.html",
        {"user": {"first_name": first_name, "username": username}},
    )
    plain_message = strip_tags(html_message)
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@treestagram.nyc")

    try:
        send_mail(
            subject, plain_message, from_email, [user_email], html_message=html_message
        )
    except Exception as e:
        # We log the error but proceed with deletion
        print(f"Error sending deletion email: {e}")

    # Log out and delete
    logout(request)
    user.delete()

    return JsonResponse({"success": True, "message": "Account deleted successfully."})


# ── Post / Like / Comment endpoints ─────────────────────────────────────────


def _post_to_dict(post, request_user):
    """Serialize a Post to a JSON-safe dict."""
    liked = False
    if request_user.is_authenticated:
        liked = post.likes.filter(user=request_user).exists()
    return {
        "id": post.id,
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
    }


def api_fetch_posts(request):
    """GET /api/posts/ — return all posts (newest first)."""
    posts = (
        Post.objects.select_related("author")
        .prefetch_related(
            "likes",
            "comments__author",
            "tagged_users",
        )
        .all()
    )
    return JsonResponse(
        {
            "success": True,
            "posts": [_post_to_dict(p, request.user) for p in posts],
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

    tree_name = data.get("tree_name", "").strip()
    if not tree_name:
        return JsonResponse(
            {"success": False, "error": "tree_name is required"}, status=400
        )

    post = Post.objects.create(
        author=request.user,
        tree_name=tree_name,
        body=data.get("body", ""),
        health=data.get("health", "Good"),
        borough=data.get("borough", ""),
        image=image,
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
    request.user.promote_if_eligible()
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
    """POST /api/posts/<id>/delete/ — delete a post (author only)."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"success": False, "error": "Post not found"}, status=404)

    if post.author_id != request.user.id:
        return JsonResponse({"success": False, "error": "Not your post"}, status=403)

    post.delete()

    # Update post count
    request.user.post_count = Post.objects.filter(author=request.user).count()
    request.user.save(update_fields=["post_count"])

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
    post.author.promote_if_eligible()
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
    """POST /api/comments/<id>/delete/ — delete a comment (author or post owner)."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    try:
        comment = Comment.objects.select_related("post").get(id=comment_id)
    except Comment.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Comment not found"}, status=404
        )

    # Allow comment author or the post author to delete
    if (
        comment.author_id != request.user.id
        and comment.post.author_id != request.user.id
    ):
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


# ── Profile-specific endpoints ───────────────────────────────────────────────
