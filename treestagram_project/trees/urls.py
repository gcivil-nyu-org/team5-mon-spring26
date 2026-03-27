from django.urls import path
from django.shortcuts import render
from . import views

urlpatterns = [
    path("map/", views.tree_map_view, name="tree_map"),
    path(
        "test_map/",
        lambda request: render(request, "trees/test_map.html"),
        name="test_map",
    ),
    # path('list/', views.tree_list_view, name='tree_list'),
    path("api/", views.trees_api, name="trees_api"),
    path("api/<int:tree_id>/", views.tree_detail_api, name="tree_detail_api"),
    path(
        "api/<int:tree_id>/dashboard/",
        views.tree_dashboard_api,
        name="tree_dashboard_api",
    ),
    path("api/search/", views.search_trees_api, name="search_trees_api"),
]
