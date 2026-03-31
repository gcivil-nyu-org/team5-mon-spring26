from django.shortcuts import render

# Create your views here.
import json
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.mail import send_mail
from django.utils import timezone
from django.core.signing import TimestampSigner
from .models import CaretakerApplication
import os
from django.conf import settings

@require_http_methods(["POST"])
def api_apply_for_caretaker(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Login required."}, status=401)

    user = request.user

    if not user.is_credible:
        return JsonResponse(
            {"error": "You need 30+ posts and 100+ likes to apply."},
            status=403,
        )

    if CaretakerApplication.objects.filter(user=user).exists():
        return JsonResponse(
            {"error": "You have already submitted an application."},
            status=400,
        )

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    motivation = data.get("motivation", "").strip()
    tree_experience = data.get("tree_experience", "").strip()

    if not motivation:
        return JsonResponse({"error": "Motivation field is required."}, status=400)

    application = CaretakerApplication.objects.create(
        user=user,
        motivation=motivation,
        experience=tree_experience,
    )

    # Generate signed approve/reject tokens
    signer = TimestampSigner()
    approve_token = signer.sign(f"approve:{application.id}")
    reject_token = signer.sign(f"reject:{application.id}")

    base_url = os.environ.get("DJANGO_SITE_DOMAIN", "localhost:8000")
    approve_url = f"http://{base_url}/api/review-application/?token={approve_token}"
    reject_url  = f"http://{base_url}/api/review-application/?token={reject_token}"

    # Email to admin
    send_mail(
        subject=f"New Caretaker Application from @{user.username}",
        message=f"""
            New caretaker application received.

            User: {user.username} ({user.email})
            Posts: {user.post_count} | Likes: {user.total_likes_received}

            --- Motivation ---
            {motivation}

            --- Tree Experience ---
            {tree_experience}

            APPROVE: {approve_url}
            REJECT:  {reject_url}
        """.strip(),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=["treestagramgetyourroots@gmail.com"],
    )

    return JsonResponse(
        {"message": "Application submitted successfully.", "id": application.id},
        status=201,
    )

@require_http_methods(["GET"])
def api_my_application_status(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Login required."}, status=401)

    try:
        application = CaretakerApplication.objects.get(user=request.user)
        return JsonResponse({
            "status": application.status,
            "submitted_at": application.submitted_at.isoformat(),
        })
    except CaretakerApplication.DoesNotExist:
        return JsonResponse({"status": None})


@require_http_methods(["GET"])
def api_review_application(request):
    token = request.GET.get("token", "")
    signer = TimestampSigner()

    try:
        # Token valid for 7 days (max_age in seconds)
        value = signer.unsign(token, max_age=60 * 60 * 24 * 7)
    except Exception:
        return JsonResponse({"error": "Invalid or expired link."}, status=400)

    decision, app_id = value.split(":")
    
    try:
        application = CaretakerApplication.objects.get(id=int(app_id))
    except CaretakerApplication.DoesNotExist:
        return JsonResponse({"error": "Application not found."}, status=404)

    if application.status != "pending":
        return JsonResponse(
            {"message": f"Application was already {application.status}."}
        )

    application.status = decision  # "approve" or "reject"
    application.reviewed_at = timezone.now()
    application.save()

    applicant = application.user

    if decision == "approve":
        applicant.role = "caretaker"
        applicant.save(update_fields=["role"])
        subject = "🌿 You've been approved as a Caretaker on Treestagram!"
        message = f"""
Hi {applicant.username},

Great news! Your application to become a Caretaker on Treestagram has been approved.

You now have caretaker privileges. Welcome to the team! 🌳

— The Treestagram Team
        """.strip()
    else:
        subject = "Your Caretaker Application on Treestagram"
        message = f"""
Hi {applicant.username},

Thank you for applying to be a Caretaker on Treestagram.

Unfortunately, your application was not approved at this time. 
You're welcome to apply again in the future as you continue contributing to the community.

— The Treestagram Team
        """.strip()

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[applicant.email],
    )

    return JsonResponse({"message": f"Application {decision}d. User notified by email."})

# import json
# from django.http import JsonResponse
# from django.views.decorators.http import require_http_methods
# from django.utils import timezone
# from .models import CaretakerApplication
# from django.core.mail import send_mail
# from django.conf import settings

# @require_http_methods(["POST"])
# def api_apply_for_caretaker(request):
#     if not request.user.is_authenticated:
#         return JsonResponse({"error": "Login required."}, status=401)

#     user = request.user

#     # Assuming you have a property or method to check credibility
#     # if not user.is_credible:
#     #     return JsonResponse({"error": "You need 30+ posts and 100+ likes to apply."}, status=403)

#     if CaretakerApplication.objects.filter(user=user, status="pending").exists():
#         return JsonResponse({"error": "You already have a pending application."}, status=400)

#     try:
#         data = json.loads(request.body)
#     except json.JSONDecodeError:
#         return JsonResponse({"error": "Invalid JSON."}, status=400)

#     motivation = data.get("motivation", "").strip()
#     tree_experience = data.get("tree_experience", "").strip()

#     if not motivation:
#         return JsonResponse({"error": "Motivation field is required."}, status=400)

#     application = CaretakerApplication.objects.create(
#         user=user,
#         motivation=motivation,
#         experience=tree_experience,
#     )

#     return JsonResponse({"message": "Application submitted successfully.", "id": application.id}, status=201)


# @require_http_methods(["GET"])
# def api_get_pending_applications(request):
#     if not request.user.is_authenticated or request.user.role != "admin":
#         return JsonResponse({"error": "Unauthorized. Admin access required."}, status=403)

#     # Fetch pending apps and prefetch user data to avoid N+1 queries
#     apps = CaretakerApplication.objects.filter(status="pending").select_related("user")
    
#     data = []
#     for app in apps:
#         data.append({
#             "id": app.id,
#             "username": app.user.username,
#             "motivation": app.motivation,
#             "treeExperience": app.experience,
#             "submitted_at": app.submitted_at.isoformat(),
#         })

#     return JsonResponse({"applications": data}, status=200)


# @require_http_methods(["POST"])
# def api_review_application(request):
#     if not request.user.is_authenticated or request.user.role != "admin":
#         return JsonResponse({"error": "Unauthorized. Admin access required."}, status=403)

#     try:
#         data = json.loads(request.body)
#     except json.JSONDecodeError:
#         return JsonResponse({"error": "Invalid JSON."}, status=400)

#     app_id = data.get("application_id")
#     action = data.get("action")  # Expected: "approved" or "rejected"

#     if action not in ["approved", "rejected"]:
#         return JsonResponse({"error": "Invalid action."}, status=400)

#     try:
#         application = CaretakerApplication.objects.get(id=app_id)
#     except CaretakerApplication.DoesNotExist:
#         return JsonResponse({"error": "Application not found."}, status=404)

#     if application.status != "pending":
#         return JsonResponse({"error": f"Application was already {application.status}."}, status=400)

#     # Update application
#     application.status = action
#     application.reviewed_at = timezone.now()
#     application.reviewed_by = request.user
#     application.save()

#     applicant = application.user

#     # Update user role if approved
#     if action == "approved":
#         applicant.role = "caretaker"
#         applicant.save(update_fields=["role"])
#         subject = "🌿 You've been approved as a Caretaker on Treestagram!"
#         message = f"Hi {applicant.username},\n\nGreat news! Your application to become a Caretaker has been approved. Welcome to the team! 🌳"
#     else:
#         subject = "Your Caretaker Application on Treestagram"
#         message = f"Hi {applicant.username},\n\nThank you for applying. Unfortunately, your application was not approved at this time. Keep contributing and try again later!"

#     # We keep the email to the USER to let them know the decision
#     send_mail(
#         subject=subject,
#         message=message,
#         from_email=settings.DEFAULT_FROM_EMAIL,
#         recipient_list=[applicant.email],
#         fail_silently=True,
#     )

#     return JsonResponse({"message": f"Application {action} successfully."})