from django.shortcuts import render
from django.http import JsonResponse, Http404
from .models import Tree
from posts.models import Post, TreeFollow
import json


def tree_map_view(request):
    trees = Tree.objects.all().values("tree_id", "spc_common", "latitude", "longitude")[
        :10
    ]
    trees_json = json.dumps(list(trees))
    return render(request, "trees/map.html", {"trees_json": trees_json})


# JSON API view for testing
def tree_list_view(request):
    trees = Tree.objects.all().values("tree_id", "spc_common", "latitude", "longitude")
    return JsonResponse(list(trees), safe=False)


def trees_api(request):
    try:
        min_lat = float(request.GET.get("min_lat", -90))
        max_lat = float(request.GET.get("max_lat", 90))
        min_lng = float(request.GET.get("min_lng", -180))
        max_lng = float(request.GET.get("max_lng", 180))
        limit = int(request.GET.get("limit", 750))
        offset = int(request.GET.get("offset", 0))
    except (ValueError, TypeError):
        return JsonResponse([], safe=False)

    qs = (
        Tree.objects.filter(
            latitude__gte=min_lat,
            latitude__lte=max_lat,
            longitude__gte=min_lng,
            longitude__lte=max_lng,
        )
        .order_by("tree_id")
        .values("tree_id", "latitude", "longitude", "spc_common")
    )

    return JsonResponse(list(qs[offset : offset + limit]), safe=False)


def tree_detail_api(request, tree_id):
    try:
        t = Tree.objects.get(tree_id=tree_id)
        data = {
            "tree_id": t.tree_id,
            "spc_common": t.spc_common,
            "spc_latin": t.spc_latin,
            "created_at": t.created_at,
            "tree_dbh": t.tree_dbh,
            "stump_diam": t.stump_diam,
            "curb_loc": t.curb_loc,
            "status": t.status,
            "health": t.health,
            "sidewalk": t.sidewalk,
            "problems": t.problems,
            "root_stone": t.root_stone,
            "root_grate": t.root_grate,
            "root_other": t.root_other,
            "trunk_wire": t.trunk_wire,
            "trnk_light": t.trnk_light,
            "trnk_other": t.trnk_other,
            "brch_light": t.brch_light,
            "brch_shoe": t.brch_shoe,
            "brch_other": t.brch_other,
            "address": t.address,
            "zip_city": t.zip_city,
            "borough": t.borough,
            "latitude": t.latitude,
            "longitude": t.longitude,
        }
        return JsonResponse(data)
    except Tree.DoesNotExist:
        raise Http404("Tree not found")


def tree_dashboard_api(request, tree_id):
    """GET /trees/api/<tree_id>/dashboard/ — full dashboard data."""
    try:
        t = Tree.objects.get(tree_id=tree_id)
    except Tree.DoesNotExist:
        raise Http404("Tree not found")

    # Base tree data (same as tree_detail_api)
    data = {
        "tree_id": t.tree_id,
        "spc_common": t.spc_common,
        "spc_latin": t.spc_latin,
        "created_at": t.created_at,
        "tree_dbh": t.tree_dbh,
        "stump_diam": t.stump_diam,
        "curb_loc": t.curb_loc,
        "status": t.status,
        "health": t.health,
        "sidewalk": t.sidewalk,
        "problems": t.problems,
        "root_stone": t.root_stone,
        "root_grate": t.root_grate,
        "root_other": t.root_other,
        "trunk_wire": t.trunk_wire,
        "trnk_light": t.trnk_light,
        "trnk_other": t.trnk_other,
        "brch_light": t.brch_light,
        "brch_shoe": t.brch_shoe,
        "brch_other": t.brch_other,
        "address": t.address,
        "zip_city": t.zip_city,
        "borough": t.borough,
        "latitude": t.latitude,
        "longitude": t.longitude,
    }

    # Posts for this tree (using tree__tree_id because the URL passes the public NYC tree_id, not the internal DB id)
    tree_posts = Post.objects.filter(tree__tree_id=tree_id).order_by("-created_at")
    posts_list = []
    photos = []
    for p in tree_posts:
        post_data = {
            "id": p.id,
            "content": p.body or "",
            "author_username": p.author.username,
            "created_at": p.created_at.isoformat(),
            "likes_count": p.likes.count(),
            "comments_count": p.comments.count(),
            "image_url": p.image if p.image else None,
        }
        posts_list.append(post_data)
        if p.image:
            photos.append(p.image)

    data["posts"] = posts_list
    data["post_count"] = len(posts_list)
    data["photos"] = photos
    data["photo_count"] = len(photos)
    data["follower_count"] = TreeFollow.objects.filter(tree__tree_id=tree_id).count()


def search_trees_api(request):
    # Get query parameters
    tree_id = request.GET.get("tree_id", "").strip()
    spc_common = request.GET.get("spc_common", "").strip()
    spc_latin = request.GET.get("spc_latin", "").strip()
    status = request.GET.get("status", "").strip()
    health = request.GET.get("health", "").strip()
    borough = request.GET.get("borough", "").strip()

    offset = int(request.GET.get("offset", 0))
    limit = int(request.GET.get("limit", 10))

    # Start with all trees
    queryset = Tree.objects.all()

    # Filter only if field is filled
    if tree_id:
        if tree_id.isdigit():
            queryset = queryset.filter(tree_id=int(tree_id))
        else:
            return JsonResponse({"results": [], "count": 0})
    if spc_common:
        queryset = queryset.filter(spc_common__icontains=spc_common)
    if spc_latin:
        queryset = queryset.filter(spc_latin__icontains=spc_latin)
    if status:
        queryset = queryset.filter(status__icontains=status)
    if health:
        queryset = queryset.filter(health__icontains=health)
    if borough:
        queryset = queryset.filter(borough__icontains=borough)

    total_count = queryset.count()
    trees = queryset.values(
        "tree_id",
        "spc_common",
        "spc_latin",
        "status",
        "health",
        "borough",
        "latitude",
        "longitude",
    )[offset : offset + limit]

    return JsonResponse({"results": list(trees), "count": total_count})


def svelte_app(request):
    """
    This single view serves the compiled Svelte index.html.
    Svelte takes over routing (login, signup, home) from here.
    """
    return render(request, "index.html")
