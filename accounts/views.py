from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ProfileForm, RegistrationForm
from .models import Profile


def register(request):
    """Create a new I-V Tree user account and profile."""

    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)

        if form.is_valid():
            user = form.save()

            Profile.objects.get_or_create(user=user)

            messages.success(
                request,
                'Your I-V Tree account has been created successfully.'
            )

            return redirect('accounts:login')
    else:
        form = RegistrationForm()

    return render(
        request,
        'accounts/register.html',
        {'form': form},
    )


@login_required
def profile(request):
    """Allow a logged-in user to view and update their profile."""

    user_profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == 'POST':
        form = ProfileForm(
            request.POST,
            instance=user_profile,
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Your profile has been updated.'
            )

            return redirect('accounts:profile')
    else:
        form = ProfileForm(instance=user_profile)

    return render(
        request,
        'accounts/profile.html',
        {
            'form': form,
            'profile': user_profile,
            'avatar_options': Profile.Avatar.choices,
        },
    )