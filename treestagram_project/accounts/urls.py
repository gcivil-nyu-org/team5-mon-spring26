from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    # REMOVED: path('', views.home_view, name='home')
    # Allauth email confirmation override
    path(
        "accounts/confirm-email/<key>/",
        views.CustomConfirmEmailView.as_view(),
        name="account_confirm_email",
    ),
]
