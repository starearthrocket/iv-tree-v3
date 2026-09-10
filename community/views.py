from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

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


def post_detail(request, pk):
    post = get_object_or_404(
        CommunityPost.objects.select_related('author'),
        pk=pk,
    )

    if not post.is_published:
        if request.user != post.author:
            raise Http404

    return render(
        request,
        'community/post_detail.html',
        {
            'post': post,
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

            return redirect(
                'community:post_detail',
                pk=post.pk,
            )
    else:
        form = CommunityPostForm()

    return render(
        request,
        'community/post_form.html',
        {
            'form': form,
            'page_title': 'Create a community post',
            'button_text': 'Publish Post',
        },
    )


@login_required
def post_edit(request, pk):
    post = get_object_or_404(
        CommunityPost,
        pk=pk,
        author=request.user,
    )

    if request.method == 'POST':
        form = CommunityPostForm(
            request.POST,
            request.FILES,
            instance=post,
        )

        if form.is_valid():
            post = form.save()

            messages.success(
                request,
                'Your community post has been updated.',
            )

            return redirect(
                'community:post_detail',
                pk=post.pk,
            )
    else:
        form = CommunityPostForm(
            instance=post,
        )

    return render(
        request,
        'community/post_form.html',
        {
            'form': form,
            'page_title': 'Edit community post',
            'button_text': 'Save Changes',
        },
    )


@login_required
def post_delete(request, pk):
    post = get_object_or_404(
        CommunityPost,
        pk=pk,
        author=request.user,
    )

    if request.method == 'POST':
        post.delete()

        messages.success(
            request,
            'Your community post has been deleted.',
        )

        return redirect('community:post_list')

    return render(
        request,
        'community/post_confirm_delete.html',
        {
            'post': post,
        },
    )