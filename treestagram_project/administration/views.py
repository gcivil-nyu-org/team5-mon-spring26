import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_GET
from django.utils import timezone
from .models import TreeChangeRequest


@require_http_methods(["POST"])
def api_submit_change_request(request):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    if request.user.role not in ("caretaker", "admin"):
        return JsonResponse({"success": False, "error": "Caretakers only"}, status=403)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    tree_id = str(data.get("tree_id", "")).strip()
    if not tree_id:
        return JsonResponse({"success": False, "error": "Tree ID is required"}, status=400)

    req = TreeChangeRequest.objects.create(
        submitted_by=request.user,
        tree_id=tree_id,
        curb_loc=data.get("curb_loc", ""),
        status=data.get("status", ""),
        health=data.get("health", ""),
        sidewalk=data.get("sidewalk", ""),
        root_stone=data.get("root_stone", ""),
        root_grate=data.get("root_grate", ""),
        root_other=data.get("root_other", ""),
        trunk_wire=data.get("trunk_wire", ""),
        trnk_light=data.get("trnk_light", ""),
        trnk_other=data.get("trnk_other", ""),
        brch_light=data.get("brch_light", ""),
        brch_shoe=data.get("brch_shoe", ""),
        brch_other=data.get("brch_other", ""),
        tree_dbh=data.get("tree_dbh", ""),
        stump_diam=data.get("stump_diam", ""),
        problems=",".join(data.get("problems", [])),
        notes=data.get("notes", ""),
    )

    return JsonResponse({"success": True, "id": req.id}, status=201)


@require_GET
def api_get_change_requests(request):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    if request.user.role != "admin":
        return JsonResponse({"success": False, "error": "Admins only"}, status=403)

    requests_qs = (
        TreeChangeRequest.objects.filter(status_field="pending")
        .select_related("submitted_by")
        .order_by("-submitted_at")
    )

    return JsonResponse({
        "success": True,
        "requests": [
            {
                "id": r.id,
                "tree_id": r.tree_id,
                "submitted_by": r.submitted_by.username,
                "submitted_at": r.submitted_at.isoformat(),
                "notes": r.notes,
                "curb_loc": r.curb_loc,
                "status": r.status,
                "health": r.health,
                "sidewalk": r.sidewalk,
                "root_stone": r.root_stone,
                "root_grate": r.root_grate,
                "root_other": r.root_other,
                "trunk_wire": r.trunk_wire,
                "trnk_light": r.trnk_light,
                "trnk_other": r.trnk_other,
                "brch_light": r.brch_light,
                "brch_shoe": r.brch_shoe,
                "brch_other": r.brch_other,
                "tree_dbh": r.tree_dbh,
                "stump_diam": r.stump_diam,
                "problems": r.problems,
            }
            for r in requests_qs
        ]
    })


@require_http_methods(["POST"])
def api_dismiss_change_request(request, request_id):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "Login required"}, status=401)

    if request.user.role != "admin":
        return JsonResponse({"success": False, "error": "Admins only"}, status=403)

    try:
        req = TreeChangeRequest.objects.get(id=request_id)
    except TreeChangeRequest.DoesNotExist:
        return JsonResponse({"success": False, "error": "Request not found"}, status=404)

    req.status_field = "dismissed"
    req.dismissed_at = timezone.now()
    req.dismissed_by = request.user
    req.save(update_fields=["status_field", "dismissed_at", "dismissed_by"])

    return JsonResponse({"success": True})