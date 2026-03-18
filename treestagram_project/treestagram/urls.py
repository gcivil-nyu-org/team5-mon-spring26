"""
URL configuration for treestagram project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import os
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.views.static import serve as static_serve

def reset_password_redirect(request, uidb64, token):
    svelte_path = f'/reset-password/{uidb64}/{token}'
    base_url = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
    return redirect(f'{base_url}{svelte_path}')

from accounts.views import svelte_app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('accounts.api_urls')),
    path('reset-password/<uidb64>/<token>/', reset_password_redirect, name='reset-password-redirect'),
    path('accounts/', include('allauth.urls')),
    path('', include('accounts.urls')),
    # Serve uploaded media files (images etc.) — works regardless of DEBUG setting
    re_path(r'^media/(?P<path>.*)$', static_serve, {'document_root': settings.MEDIA_ROOT}),
    # Catch-all — serve Svelte SPA (must be last!)
    re_path(r'^(?!api/|admin/|accounts/|media/).*$', TemplateView.as_view(template_name='index.html')),
    re_path(r'^.*$', svelte_app, name='svelte_app'),
]
