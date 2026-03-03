"""
accounts/api_views.py
JSON API endpoints consumed by the Svelte frontend.
"""
import json
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from .forms import SignupForm
from .models import User


def user_to_dict(user):
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'borough': user.borough,
        'role': user.role,
        'post_count': user.post_count,
        'total_likes_received': user.total_likes_received,
        'leaves': user.leaves,
    }


@ensure_csrf_cookie
def csrf_view(request):
    """Hit this endpoint to get the CSRF cookie set."""
    return JsonResponse({'csrfToken': get_token(request)})


@require_http_methods(["POST"])
def api_signup(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    form = SignupForm(data)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return JsonResponse({'success': True, 'user': user_to_dict(user)})
    else:
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)


@require_http_methods(["POST"])
def api_login(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return JsonResponse({'success': False, 'error': 'Username and password required.'}, status=400)

    user = authenticate(request, username=username, password=password)
    if user:
        login(request, user)
        return JsonResponse({'success': True, 'user': user_to_dict(user)})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid username or password.'}, status=401)


@require_http_methods(["POST"])
def api_logout(request):
    logout(request)
    return JsonResponse({'success': True})


def api_check_username(request):
    """Check if a username is already taken."""
    username = request.GET.get('username', '').strip()
    if len(username) < 3:
        return JsonResponse({'available': False, 'error': 'Too short'})
    taken = User.objects.filter(username__iexact=username).exists()
    return JsonResponse({'available': not taken})


def api_me(request):
    """Return current user info if logged in."""
    if request.user.is_authenticated:
        return JsonResponse({'success': True, 'user': user_to_dict(request.user)} | user_to_dict(request.user))
    return JsonResponse({'success': False}, status=401)
