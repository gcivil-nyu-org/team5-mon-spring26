from django.shortcuts import render

def svelte_app(request):
    """
    This single view serves the compiled Svelte index.html.
    Svelte takes over routing (login, signup, home) from here.
    """
    return render(request, 'index.html')