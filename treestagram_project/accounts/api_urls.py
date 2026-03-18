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
    # ── Post / Like / Comment ──
    path('posts/',                     api_views.api_fetch_posts,          name='api-fetch-posts'),
    path('my-posts/',                  api_views.api_fetch_my_posts,       name='api-my-posts'),
    path('my-tagged-posts/',           api_views.api_fetch_my_tagged_posts,name='api-my-tagged-posts'),
    path('posts/create/',              api_views.api_create_post,          name='api-create-post'),
    path('posts/<int:post_id>/delete/',api_views.api_delete_post,          name='api-delete-post'),
    path('posts/<int:post_id>/like/',  api_views.api_toggle_like,          name='api-toggle-like'),
    path('posts/<int:post_id>/comment/',api_views.api_add_comment,         name='api-add-comment'),
    path('comments/<int:comment_id>/edit/',   api_views.api_edit_comment,  name='api-edit-comment'),
    path('comments/<int:comment_id>/delete/', api_views.api_delete_comment,name='api-delete-comment'),
    # ── Notifications ──
    path('notifications/',                api_views.api_notifications,             name='api-notifications'),
    path('notifications/unread-count/',   api_views.api_notifications_unread_count, name='api-notifications-unread-count'),
    path('notifications/mark-read/',      api_views.api_notifications_mark_read,    name='api-notifications-mark-read'),
    path('notifications/mark-all-read/',  api_views.api_notifications_mark_all_read,name='api-notifications-mark-all-read'),
]
