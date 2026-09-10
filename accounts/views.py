from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render

from community.models import CommunityPost
from reports.models import ProgressUpdate, TreeReport

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


@login_required
def dashboard(request):
    """Show the logged-in user's I-V Tree activity."""

    user_profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    my_reports = TreeReport.objects.filter(
        owner=request.user
    )

    my_updates = ProgressUpdate.objects.filter(
        author=request.user
    )

    my_posts = CommunityPost.objects.filter(
        author=request.user
    )

    context = {
        'profile': user_profile,
        'my_reports': my_reports,
        'my_updates': my_updates,
        'my_posts': my_posts,
        'report_count': my_reports.count(),
        'update_count': my_updates.count(),
        'post_count': my_posts.count(),
    }

    return render(
        request,
        'accounts/dashboard.html',
        context,
    )


def public_profile(request, username):
    """Show a user's public I-V Tree activity."""

    profile_user = get_object_or_404(
        User,
        username=username,
    )

    user_profile, created = Profile.objects.get_or_create(
        user=profile_user,
    )

    public_reports = TreeReport.objects.filter(
        owner=profile_user,
        visibility=TreeReport.Visibility.PUBLIC,
    )

    published_posts = CommunityPost.objects.filter(
        author=profile_user,
        is_published=True,
    )

    context = {
        'profile_user': profile_user,
        'profile': user_profile,
        'public_reports': public_reports,
        'published_posts': published_posts,
        'report_count': public_reports.count(),
        'post_count': published_posts.count(),
    }

    return render(
        request,
        'accounts/public_profile.html',
        context,
    )