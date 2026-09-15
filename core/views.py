from django.shortcuts import render


def home(request):
    """Display the I-V Tree homepage."""

    return render(
        request,
        'core/home.html',
    )


def custom_404(request, exception):
    """Display the custom page-not-found response."""

    return render(
        request,
        'errors/404.html',
        status=404,
    )


def custom_500(request):
    """Display the custom server-error response."""

    return render(
        request,
        'errors/500.html',
        status=500,
    )