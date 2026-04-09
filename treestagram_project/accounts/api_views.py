"""
accounts/api_views.py
JSON API endpoints consumed by the Svelte frontend.
"""

import json
import logging
import os
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.core.mail import send_mail
from django.core.signing import TimestampSigner, SignatureExpired, BadSignature
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.shortcuts import redirect
from django.conf import settings
from .forms import SignupForm
from .models import User

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
        "credible_post_threshold": user.CREDIBLE_POST_THRESHOLD,
        "credible_like_threshold": user.CREDIBLE_LIKE_THRESHOLD,
    }


def send_confirmation_email(user):
    """Build and send a confirmation email using Django's signing framework.
    No dependency on the Sites framework or allauth's send_confirmation."""
    signer = TimestampSigner()
    token = signer.sign(user.pk)

    base_url = os.environ.get("DJANGO_SITE_DOMAIN", "localhost")
    confirm_url = f"http://{base_url}/api/confirm-email/{token}/"

    subject = "Welcome to Treestagram — Confirm your email"
    html_message = render_to_string(
        "accounts/confirmation_email.html",
        {
            "user": user,
            "confirm_url": confirm_url,
        },
    )
    plain_message = strip_tags(html_message)
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@treestagram.nyc")

    send_mail(
        subject,
        plain_message,
        from_email,
        [user.email],
        html_message=html_message,
    )


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
            send_confirmation_email(user)
            logger.info("Confirmation email sent to %s", user.email)
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


def api_confirm_email(request, token):
    """GET /api/confirm-email/<token>/ — verify token, activate user, redirect to frontend."""
    signer = TimestampSigner()
    try:
        # Token expires after 3 days
        user_pk = signer.unsign(token, max_age=60 * 5)
        user = User.objects.get(pk=user_pk)
        user.is_active = True
        user.save(update_fields=["is_active"])
        logger.info("Email confirmed for user %s", user.email)

        frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")
        return redirect(f"{frontend_url}/login?confirmed=true")

    except SignatureExpired:
        return JsonResponse(
            {
                "success": False,
                "error": "Confirmation link has expired. Please sign up again.",
            },
            status=400,
        )
    except (BadSignature, User.DoesNotExist):
        return JsonResponse(
            {"success": False, "error": "Invalid confirmation link."},
            status=400,
        )


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
        user = User.objects.get(email__iexact=email, is_active=False)
        send_confirmation_email(user)
        return JsonResponse({"success": True, "message": "Verification email sent!"})
    except User.DoesNotExist:
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

    if request.content_type == "application/json":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    else:
        data = request.POST

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

    if not user.check_password(current_password):
        return JsonResponse(
            {"success": False, "error": "Current password incorrect."}, status=400
        )

    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError

    try:
        validate_password(new_password, user)
    except ValidationError as e:
        return JsonResponse(
            {"success": False, "error": " ".join(e.messages)}, status=400
        )

    from django.contrib.auth import update_session_auth_hash

    user.set_password(new_password)
    user.save()
    update_session_auth_hash(request, user)

    return JsonResponse({"success": True, "message": "Password changed successfully."})


@require_http_methods(["POST"])
def api_delete_account(request):
    """Deletes the current user's account after password verification."""
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
        print(f"Error sending deletion email: {e}")

    logout(request)
    user.delete()

    return JsonResponse({"success": True, "message": "Account deleted successfully."})


# ── Profile-specific endpoints ───────────────────────────────────────────────


# becoming an admin
@require_http_methods(["POST"])
def api_become_admin(request):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    if data.get("answer") == "yEs i LOV3 trees":
        request.user.role = "admin"
        request.user.save(update_fields=["role"])
        return JsonResponse({"success": True})
    return JsonResponse({"success": False, "error": "Incorrect answer."}, status=403)


# becoming an admin


# get trees user is taking care of
def api_my_caretaker_trees(request):
    """GET /api/my-caretaker-trees/ — trees the current user is assigned to care for."""
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    from caretaker.models import CaretakerAssignment
    from trees.models import Tree

    assignments = CaretakerAssignment.objects.filter(user=request.user)
    trees = []
    for a in assignments:
        try:
            t = Tree.objects.get(tree_id=a.tree_id)
            trees.append(
                {
                    "tree_id": a.tree_id,
                    "tree_name": t.spc_common or f"Tree #{a.tree_id}",
                    "assigned_at": a.assigned_at.isoformat(),
                }
            )
        except Tree.DoesNotExist:
            pass

    return JsonResponse({"success": True, "trees": trees})


# get trees user is taking care of
