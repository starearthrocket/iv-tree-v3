from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import RegistrationForm
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