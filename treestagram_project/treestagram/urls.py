from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect


def reset_password_redirect(request, uidb64, token):
    """Redirect reset-password links from email to the Svelte frontend."""
    svelte_path = f'/reset-password/{uidb64}/{token}'
    if settings.DEBUG:
        return redirect(f'http://localhost:5173{svelte_path}')
    return redirect(svelte_path)

from accounts.views import svelte_app

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # JSON API — Svelte uses these to log in and fetch data
    path('api/', include('accounts.api_urls')),

    # THE SPA CATCH-ALL
    # Every single URL that isn't /admin or /api gets sent to Svelte.
    # If the user goes to /login, /signup, or /home, Django serves Svelte,
    # and Svelte's App.svelte router decides which component to show.
    re_path(r'^.*$', svelte_app, name='svelte_app'),
    # Redirect reset-password links from email to Svelte SPA
    path('reset-password/<uidb64>/<token>/',
         reset_password_redirect,
         name='reset-password-redirect'),

    # allauth (Google OAuth callbacks, email confirmation pages)
    path('accounts/', include('allauth.urls')),

    # Django template views (server-rendered fallback)
    path('', include('accounts.urls')),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
