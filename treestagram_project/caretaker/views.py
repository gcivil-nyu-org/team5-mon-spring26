# Create your views here.
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.mail import send_mail
from django.utils import timezone
from django.conf import settings
from .models import CaretakerApplication, CaretakerAssignment
from trees.models import Tree
from django.views.decorators.http import require_GET
from posts.models import TreeFollow


@require_http_methods(["POST"])
def api_apply_for_caretaker(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Login required."}, status=401)

    user = request.user

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    # Cast to string before stripping in case the frontend sends an integer
    tree_id = str(data.get("tree_id", "")).strip()
    motivation = data.get("motivation", "").strip()
    tree_experience = data.get("tree_experience", "").strip()

    # --- Basic Validation ---
    if not tree_id:
        return JsonResponse({"error": "Tree ID is required."}, status=400)
    if not motivation:
        return JsonResponse({"error": "Motivation field is required."}, status=400)

    # --- NEW: Check 1 - User already applied and is pending for THIS tree ---
    if CaretakerApplication.objects.filter(
        user=user, tree_id=tree_id, status="pending"
    ).exists():
        return JsonResponse(
            {"error": "You already have a pending application for this tree."},
            status=400,
        )

    # --- NEW: Check 2 - User is already a caretaker for THIS tree ---
    if CaretakerAssignment.objects.filter(user=user, tree_id=tree_id).exists():
        return JsonResponse(
            {"error": "You are already a caretaker for this tree."}, status=400
        )
    
    # --- Check 3 - Tree already has 2 caretakers ---
    if CaretakerAssignment.objects.filter(tree_id=tree_id).count() >= 2:
        return JsonResponse(
            {"error": "Caretaker slots for this tree are full."}, status=400
    )

    tree = Tree.objects.filter(tree_id=tree_id).first()
    is_following = TreeFollow.objects.filter(user=user, tree=tree).exists()

    # CHECK 3 - Trigger the error if they are NOT following the tree
    if not is_following:
        return JsonResponse(
            {"error": "You must follow the tree before applying as a caretaker."},
            status=403,
        )

    # --- Save to database ---
    application = CaretakerApplication.objects.create(
        user=user,
        tree_id=tree_id,
        motivation=motivation,
        experience=tree_experience,
    )

    return JsonResponse(
        {"message": "Application submitted successfully.", "id": application.id},
        status=201,
    )


@require_GET
def api_get_pending_applications(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized. Login required."}, status=403)

    applications = (
        CaretakerApplication.objects.filter(status="pending")
        .select_related("user")
        .order_by("-submitted_at")
    )

    return JsonResponse(
        {
            "applications": [
                {
                    "id": app.id,
                    "username": app.user.username,
                    "treeId": app.tree_id,
                    "motivation": app.motivation,
                    "treeExperience": app.experience,
                    "submitted_at": app.submitted_at.isoformat(),
                }
                for app in applications
            ]
        }
    )


@require_http_methods(["POST"])
def api_review_application(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized. Login required."}, status=403)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON."}, status=400)

    app_id = data.get("application_id")
    action = data.get("action")  # Expected: "approved" or "rejected"

    if action not in ["approved", "rejected"]:
        return JsonResponse({"error": "Invalid action."}, status=400)

    try:
        application = CaretakerApplication.objects.get(id=app_id)
    except CaretakerApplication.DoesNotExist:
        return JsonResponse({"error": "Application not found."}, status=404)

    if application.status != "pending":
        return JsonResponse(
            {"error": f"Application was already {application.status}."}, status=400
        )

    # Update application
    application.status = action
    application.reviewed_at = timezone.now()
    application.reviewed_by = request.user
    application.save()

    applicant = application.user

    # Update user role if approved
    if action == "approved":
        applicant.role = "caretaker"
        applicant.save(update_fields=["role"])

        # Create assignment for the specific tree
        if application.tree_id:
            CaretakerAssignment.objects.get_or_create(
                user=applicant, tree_id=application.tree_id
            )

        subject = "🌿 You've been approved as a Caretaker on Treestagram!"
        message = f"""Hi {applicant.username},\n\nGreat news! Your application to become a
        Caretaker has been approved. Welcome to the team! 🌳"""
    else:
        subject = "Your Caretaker Application on Treestagram"
        message = f"""Hi {applicant.username},\n\nThank you for applying. Unfortunately, your
        application was not approved at this time. Keep contributing and try again later!"""

    # We keep the email to the USER to let them know the decision
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[applicant.email],
        fail_silently=True,
    )

    return JsonResponse({"message": f"Application {action} successfully."})


@require_http_methods(["GET"])
def api_check_tree(request):
    tree_id = request.GET.get("tree_id", "").strip()

    # if not tree_id:
    #     return JsonResponse({"exists": False})
    queryset = Tree.objects.all()
    if tree_id:
        if tree_id.isdigit():
            queryset = queryset.filter(tree_id=int(tree_id))
        else:
            return JsonResponse({"exists": False})

    count = queryset.count()

    if count > 0:
        exists = True
        return JsonResponse({"exists": exists})

    else:
        return JsonResponse({"exists": False})
