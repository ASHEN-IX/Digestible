from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.contrib.auth.models import User
import requests


@login_required
def dashboard_home(request):
    """Main dashboard view"""
    # Get user stats from articles API
    try:
        response = requests.get(
            f"{settings.FASTAPI_URL}/api/v1/articles/stats/",
            cookies=request.COOKIES,
            timeout=5,
        )
        stats = response.json() if response.status_code == 200 else {}
    except:
        stats = {}

    context = {
        "stats": stats,
        "fastapi_url": settings.FASTAPI_URL,
    }
    return render(request, "dashboard/home.html", context)


@login_required
def articles_list(request):
    """Articles list view"""
    context = {
        "fastapi_url": settings.FASTAPI_URL,
    }
    return render(request, "dashboard/articles.html", context)


@login_required
def profile_view(request):
    """User profile view"""
    return render(request, "dashboard/profile.html")


def login_view(request):
    """Custom login view"""
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":
        # Handle login via API
        try:
            response = requests.post(
                f"{request.scheme}://{request.get_host()}/api/auth/login/",
                json={
                    "username": request.POST.get("username"),
                    "password": request.POST.get("password"),
                },
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # Set session from API response
                    request.session["_auth_user_id"] = str(data["user"]["id"])
                    request.session["_auth_user_backend"] = (
                        "django.contrib.auth.backends.ModelBackend"
                    )
                    messages.success(
                        request, f"Welcome back, {data['user']['username']}!"
                    )
                    return redirect("dashboard:home")
                else:
                    messages.error(request, data.get("error", "Login failed"))
            else:
                messages.error(request, "Login failed")

        except requests.RequestException:
            messages.error(request, "Unable to connect to authentication service")

    return render(request, "dashboard/login.html")


def register_view(request):
    """Registration view"""
    if request.user.is_authenticated:
        return redirect("dashboard:home")

    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        # Basic validation
        if not all([username, email, password1, password2]):
            messages.error(request, "All fields are required")
        elif password1 != password2:
            messages.error(request, "Passwords do not match")
        elif len(password1) < 8:
            messages.error(request, "Password must be at least 8 characters")
        else:
            try:
                # Create user
                user = User.objects.create_user(
                    username=username, email=email, password=password1
                )
                messages.success(
                    request, "Account created successfully! Please log in."
                )
                return redirect("dashboard:login")
            except Exception as e:
                messages.error(request, f"Registration failed: {str(e)}")

    return render(request, "dashboard/register.html")
