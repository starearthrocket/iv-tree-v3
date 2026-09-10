from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import CommunityPostForm
from .models import CommunityPost


def post_list(request):
    posts = CommunityPost.objects.filter(
        is_published=True
    ).select_related('author')

    return render(
        request,
        'community/post_list.html',
        {
            'posts': posts,
        },
    )


@login_required
def post_create(request):
    if request.method == 'POST':
        form = CommunityPostForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()

            messages.success(
                request,
                'Your community post has been created.',
            )

            return redirect('community:post_list')
    else:
        form = CommunityPostForm()

    return render(
        request,
        'community/post_form.html',
        {
            'form': form,
        },
    )