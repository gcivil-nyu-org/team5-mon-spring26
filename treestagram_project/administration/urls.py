from django.urls import path
from . import views

urlpatterns = [
    path(
        "submit-change-request/",
        views.api_submit_change_request,
        name="submit-change-request",
    ),
    path("change-requests/", views.api_get_change_requests, name="get-change-requests"),
    path(
        "dismiss-change-request/<int:request_id>/",
        views.api_dismiss_change_request,
        name="dismiss-change-request",
    ),
]
