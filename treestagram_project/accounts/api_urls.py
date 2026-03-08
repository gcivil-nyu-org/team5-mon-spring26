from django.urls import path
from . import api_views

urlpatterns = [
    path('csrf/',   api_views.csrf_view,  name='api-csrf'),
    path('signup/', api_views.api_signup, name='api-signup'),
    path('login/',  api_views.api_login,  name='api-login'),
    path('logout/', api_views.api_logout, name='api-logout'),
    path('me/',             api_views.api_me,             name='api-me'),
    path('check-username/', api_views.api_check_username, name='api-check-username'),
    path('google-login-url/', api_views.api_google_login_url, name='api-google-login-url'),
    path('resend-verification/', api_views.api_resend_verification, name='api-resend-verification'),
    path('forgot-password/', api_views.api_forgot_password, name='api-forgot-password'),
    path('verify-reset-token/<uidb64>/<token>/', api_views.api_verify_reset_token, name='api-verify-reset-token'),
    path('reset-password/<uidb64>/<token>/', api_views.api_reset_password, name='api-reset-password'),
    path('update-profile/', api_views.api_update_profile, name='api-update-profile'),
    path('change-password/', api_views.api_change_password, name='api-change-password'),
    path('verify-password/', api_views.api_verify_password, name='api-verify-password'),
    path('delete-account/', api_views.api_delete_account, name='api-delete-account'),
]
