from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import CustomUserCreationForm, CustomAuthenticationForm


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            
            # Utwórz profil SmartCARS dla nowego użytkownika
            try:
                from acars.models import SmartcarsProfile
                profile = SmartcarsProfile.get_or_create_for_user(user)
                messages.info(request, f'ACARS profile created with API key: {profile.api_key[:8]}...')
            except Exception as e:
                messages.warning(request, 'Account was created, but there was an issue setting up ACARS profile.')
            
            # Send welcome email
            try:
                send_mail(
                    'Welcome to Topsky Virtual Airlines!',
                    f'Hello {user.first_name}!\n\nYour account has been successfully created. Welcome to Topsky Virtual Airlines!\n\nHappy flying!',
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            except Exception as e:
                messages.warning(request, 'Account was created, but we couldn\'t send the welcome email.')
            
            messages.success(request, f'Account for {username} has been created! You can now log in.')
            return redirect('accounts:login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name}!')
                return redirect('accounts:dashboard')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def dashboard_view(request):
    # Pobierz lub utwórz profil SmartCARS użytkownika
    try:
        from acars.models import SmartcarsProfile
        smartcars_profile = SmartcarsProfile.get_or_create_for_user(request.user)
    except Exception as e:
        # Fallback - spróbuj utworzyć ręcznie
        try:
            from acars.models import SmartcarsProfile
            smartcars_profile = SmartcarsProfile.objects.create(user=request.user)
        except:
            smartcars_profile = None
    
    context = {
        'user': request.user,
        'smartcars_profile': smartcars_profile
    }
    return render(request, 'accounts/dashboard.html', context) 