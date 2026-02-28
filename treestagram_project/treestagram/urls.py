# treestagram/urls.py (Main folder)
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

# Import views so we can use your protected app_view
from accounts import views 

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # JSON API — consumed by the Svelte frontend
    path('api/', include('accounts.api_urls')),

    # Django template views (login, signup, logout)
    path('', include('accounts.urls')),
    
    # THE FIX: Point directly to your protected view, and name it 'svelte_app'
    re_path(r'^.*$', views.app_view, name='svelte_app'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)