from django.urls import path
from . import views

urlpatterns = [    
    path("apply-for-caretaker/", views.api_apply_for_caretaker, name="api-apply-for-caretaker"),
    # path("my-application-status/", api_views.api_my_application_status, name="api-my-application-status"),
    path("review-application/", views.api_review_application, name="api-review-application"),

    # 1. User submits an application
    path("apply-for-caretaker/", views.api_apply_for_caretaker, name="api-apply-for-caretaker"),
    
    # 2. Admin fetches the list of pending applications (NEW)
    # path("pending-applications/", views.api_get_pending_applications, name="api-pending-applications"),
    
    # 3. Admin approves or rejects an application (UPDATED to handle POST requests)
    path("review-application/", views.api_review_application, name="api-review-application"),
]