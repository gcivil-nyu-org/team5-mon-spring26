from django.shortcuts import render
from django.http import JsonResponse, Http404
from .models import Tree
import json

def tree_map_view(request):
    trees = Tree.objects.all().values('tree_id', 'spc_common', 'latitude', 'longitude')[:10]
    trees_json = json.dumps(list(trees))
    return render(request, 'trees/map.html', {'trees_json': trees_json})

from django.http import JsonResponse

# JSON API view for testing
def tree_list_view(request):
    trees = Tree.objects.all().values(
        'tree_id', 'spc_common', 'latitude', 'longitude'
    )
    return JsonResponse(list(trees), safe=False)

def trees_api(request):
    limit = request.GET.get('limit', 10)
    print("Limit param received:", limit)
    try:
        limit = int(limit)
    except ValueError:
        limit = 10

    # slice queryset
    trees = Tree.objects.all()[:limit]
    print("Returning trees:", trees.count())

    # serialize to JSON
    data = [
        {
            "tree_id": t.tree_id,
            "spc_common": t.spc_common,
            "latitude": t.latitude,
            "longitude": t.longitude,
        }
        for t in trees
    ]
    return JsonResponse(data, safe=False)

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


from django.db.models import Q

# def search_trees_api(request):
#     q = request.GET.get("q", "").strip()
#     offset = int(request.GET.get("offset", 0))
#     limit = int(request.GET.get("limit", 10))

#     if not q:
#         return JsonResponse({"results": [], "count": 0})

#     # Search by spc_common or address (case-insensitive)
#     queryset = Tree.objects.filter(
#         spc_common__icontains=q
#     ).order_by("tree_id")

#     total_count = queryset.count()
#     trees = queryset[offset: offset + limit]

#     data = [
#         {
#             "tree_id": t.tree_id,
#             "spc_common": t.spc_common,
#             "latitude": t.latitude,
#             "longitude": t.longitude,
#         }
#         for t in trees
#     ]

#     return JsonResponse({"results": data, "count": total_count})

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
    trees = queryset[offset: offset + limit]

    data = [
        {
            "tree_id": t.tree_id,
            "spc_common": t.spc_common,
            "spc_latin": t.spc_latin,
            "status": t.status,
            "health": t.health,
            "borough": t.borough,
            "latitude": t.latitude,
            "longitude": t.longitude,
        }
        for t in trees
    ]

    return JsonResponse({"results": data, "count": total_count})

def svelte_app(request):
    """
    This single view serves the compiled Svelte index.html.
    Svelte takes over routing (login, signup, home) from here.
    """
    return render(request, 'index.html')
