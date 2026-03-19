from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
import os

from .forms import SignupForm, LoginForm


@require_http_methods(["GET", "POST"])
def signup_view(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(
                request,
                f"Welcome to Treestagram, {user.username}! 🌳 Start exploring NYC trees."
            )
            return redirect('home')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = SignupForm()

    return render(request, 'accounts/signup.html', {'form': form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}! 🌿")
            # Redirect to 'next' param if provided, else home
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm(request)

    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.info(request, "You've been logged out. See you soon! 🍃")
    return redirect('login')


@login_required
def home_view(request):
    """Placeholder home view — replace with real feed later."""
    return render(request, 'accounts/home.html', {'user': request.user})

def svelte_app(request):
    """
    This single view serves the compiled Svelte index.html.
    Svelte takes over routing (login, signup, home) from here.
    """
    context = {
        'frontend_url': get_frontend_url()
    }
    return render(request, 'index.html', context)

# this is for email confirmation ------------------------------------------------
def get_frontend_url():
    # Use FRONTEND_URL env variable if set, otherwise default to localhost
    return os.environ.get('FRONTEND_URL', 'http://localhost:5173')


from allauth.account.views import ConfirmEmailView
class CustomConfirmEmailView(ConfirmEmailView):
    """
    Overrides Allauth confirm email view to pass frontend URL to template
    """
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['frontend_url'] = get_frontend_url()
        return context
# this is for email confirmation ------------------------------------------------
