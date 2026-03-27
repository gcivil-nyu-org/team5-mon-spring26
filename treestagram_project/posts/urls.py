from django.urls import path
from . import api_views

urlpatterns = [
    # ── Post / Like / Comment ──
    path("posts/", api_views.api_fetch_posts, name="api-fetch-posts"),
    path("my-posts/", api_views.api_fetch_my_posts, name="api-my-posts"),
    path(
        "my-tagged-posts/",
        api_views.api_fetch_my_tagged_posts,
        name="api-my-tagged-posts",
    ),
    path("posts/create/", api_views.api_create_post, name="api-create-post"),
    path("validate-tree/", api_views.api_validate_tree, name="api-validate-tree"),
    path(
        "posts/<int:post_id>/delete/", api_views.api_delete_post, name="api-delete-post"
    ),
    path(
        "posts/<int:post_id>/like/", api_views.api_toggle_like, name="api-toggle-like"
    ),
    path(
        "posts/<int:post_id>/comment/",
        api_views.api_add_comment,
        name="api-add-comment",
    ),
    path(
        "comments/<int:comment_id>/edit/",
        api_views.api_edit_comment,
        name="api-edit-comment",
    ),
    path(
        "comments/<int:comment_id>/delete/",
        api_views.api_delete_comment,
        name="api-delete-comment",
    ),
    # ── Notifications ──
    path("notifications/", api_views.api_notifications, name="api-notifications"),
    path(
        "notifications/unread-count/",
        api_views.api_notifications_unread_count,
        name="api-notifications-unread-count",
    ),
    path(
        "notifications/mark-read/",
        api_views.api_notifications_mark_read,
        name="api-notifications-mark-read",
    ),
    path(
        "notifications/mark-all-read/",
        api_views.api_notifications_mark_all_read,
        name="api-notifications-mark-all-read",
    ),
    # ── Tree Follow ──
    path(
        "trees/<int:tree_id>/follow/",
        api_views.api_toggle_tree_follow,
        name="api-toggle-tree-follow",
    ),
    path(
        "trees/<int:tree_id>/posts/",
        api_views.api_fetch_tree_posts,
        name="api-fetch-tree-posts",
    ),
    path(
        "my-followed-trees/",
        api_views.api_my_followed_trees,
        name="api-my-followed-trees",
    ),
]
