from django.urls import path
from . import views

urlpatterns = [
    path(
        "apply-for-caretaker/",
        views.api_apply_for_caretaker,
        name="api-apply-for-caretaker",
    ),
    path(
        "review-application/",
        views.api_review_application,
        name="api-review-application",
    ),
    # 1. User submits an application
    # duplicate path above: path("apply-for-caretaker/", views.api_apply_for_caretaker, name="api-apply-for-caretaker"),
    # 2. Admin fetches the list of pending applications
    path(
        "pending-applications/",
        views.api_get_pending_applications,
        name="api-pending-applications",
    ),
    # Frontend endpoints
    path("caretaker-applications/apply/", views.api_apply_for_caretaker),
    path("caretaker-applications/pending/", views.api_get_pending_applications),
    path("caretaker-applications/review/", views.api_review_application),
    path("check-tree/", views.api_check_tree, name="api-check-tree"),
]
