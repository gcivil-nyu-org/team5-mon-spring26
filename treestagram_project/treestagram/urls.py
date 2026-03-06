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

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect


def reset_password_redirect(request, uidb64, token):
    """Redirect reset-password links from email to the Svelte frontend."""
    svelte_path = f'/reset-password/{uidb64}/{token}'
    if settings.DEBUG:
        return redirect(f'http://localhost:5173{svelte_path}')
    return redirect(svelte_path)


urlpatterns = [
    path('admin/', admin.site.urls),
                  # JSON API — consumed by the Svelte frontend
                  path('api/', include('accounts.api_urls')),

                  # Redirect reset-password links from email to Svelte SPA
                  path('reset-password/<uidb64>/<token>/',
                       reset_password_redirect,
                       name='reset-password-redirect'),

                  # allauth (Google OAuth callbacks, email confirmation pages)
                  path('accounts/', include('allauth.urls')),

                  # Django template views (server-rendered fallback)
                  path('', include('accounts.urls')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
