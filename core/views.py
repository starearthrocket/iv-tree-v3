from django.conf import settings
from django.shortcuts import render

from reports.models import TreeReport


def home(request):
    """Display the I-V Tree homepage."""

    recent_reports = (
        TreeReport.objects
        .filter(
            visibility=TreeReport.Visibility.PUBLIC
        )
        .select_related('owner')[:3]
    )

    return render(
        request,
        'core/home.html',
        {
            'recent_reports': recent_reports,
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
            'google_maps_map_id': settings.GOOGLE_MAPS_MAP_ID,
        },
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