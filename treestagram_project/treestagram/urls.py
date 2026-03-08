from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
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

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)