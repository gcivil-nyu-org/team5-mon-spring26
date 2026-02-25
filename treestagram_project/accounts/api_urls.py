from django.urls import path
from . import api_views

urlpatterns = [
    path('csrf/',   api_views.csrf_view,  name='api-csrf'),
    path('signup/', api_views.api_signup, name='api-signup'),
    path('login/',  api_views.api_login,  name='api-login'),
    path('logout/', api_views.api_logout, name='api-logout'),
    path('me/',     api_views.api_me,     name='api-me'),
]
