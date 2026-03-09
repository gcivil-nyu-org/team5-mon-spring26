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
    
    # 1. JSON API — Svelte uses these to log in and fetch data
    path('api/', include('accounts.api_urls')),

    # 2. Redirect reset-password links from email to Svelte SPA
    path('reset-password/<uidb64>/<token>/',
         reset_password_redirect,
         name='reset-password-redirect'),

    # 3. allauth (Google OAuth callbacks, email confirmation pages)
    path('accounts/', include('allauth.urls')),

    # 4. Django template views (server-rendered fallback)
    # Be careful here: if accounts.urls contains a root path (''), 
    # it might catch traffic meant for Svelte. It's safer to prefix this.
    path('server/', include('accounts.urls')), 

    # 5. THE SPA CATCH-ALL (Must be absolute last!)
    # Every single URL that isn't matched above gets sent to Svelte.
    re_path(r'^.*$', svelte_app, name='svelte_app'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)