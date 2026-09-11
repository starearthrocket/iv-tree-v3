import json
import logging
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ProgressUpdateForm, TreeReportForm
from .models import ProgressUpdate, TreeReport


logger = logging.getLogger(__name__)


def convert_to_what3words(latitude, longitude):
    """Convert latitude and longitude into a what3words address."""

    if not settings.WHAT3WORDS_API_KEY:
        return None

    coordinates = f'{latitude},{longitude}'

    query = urllib.parse.urlencode(
        {
            'coordinates': coordinates,
            'language': 'en',
        }
    )

    url = (
        'https://api.what3words.com/v3/convert-to-3wa?'
        f'{query}'
    )

    request = urllib.request.Request(
        url,
        headers={
            'X-Api-Key': settings.WHAT3WORDS_API_KEY,
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=5,
        ) as response:
            data = json.load(response)

        words = data.get('words')

        if words:
            return f'///{words}'

    except (
        urllib.error.HTTPError,
        urllib.error.URLError,
        TimeoutError,
        json.JSONDecodeError,
    ) as error:
        logger.warning(
            'what3words conversion failed: %s',
            error,
        )

    return None


def convert_from_what3words(three_word_address):
    """Convert a what3words address into coordinates."""

    if not settings.WHAT3WORDS_API_KEY:
        return None

    words = three_word_address.strip()

    if words.startswith('///'):
        words = words[3:]

    query = urllib.parse.urlencode(
        {
            'words': words,
        }
    )

    url = (
        'https://api.what3words.com/v3/convert-to-coordinates?'
        f'{query}'
    )

    request = urllib.request.Request(
        url,
        headers={
            'X-Api-Key': settings.WHAT3WORDS_API_KEY,
        },
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=5,
        ) as response:
            data = json.load(response)

        coordinates = data.get('coordinates')
        returned_words = data.get('words')

        if not coordinates or not returned_words:
            return None

        return {
            'latitude': coordinates.get('lat'),
            'longitude': coordinates.get('lng'),
            'what3words': f'///{returned_words}',
            'country': data.get('country', ''),
            'nearest_place': data.get('nearestPlace', ''),
        }

    except urllib.error.HTTPError as error:
        logger.warning(
            'what3words address lookup failed: %s',
            error,
        )

    except (
        urllib.error.URLError,
        TimeoutError,
        json.JSONDecodeError,
    ) as error:
        logger.warning(
            'what3words lookup unavailable: %s',
            error,
        )

    return None


@login_required
@require_POST
def what3words_lookup(request):
    """Return coordinates for a submitted what3words address."""

    three_word_address = request.POST.get(
        'what3words',
        '',
    ).strip()

    if not three_word_address:
        return JsonResponse(
            {
                'success': False,
                'message': (
                    'Enter a what3words address first.'
                ),
            },
            status=400,
        )

    result = convert_from_what3words(
        three_word_address
    )

    if not result:
        return JsonResponse(
            {
                'success': False,
                'message': (
                    'That what3words address could not be found. '
                    'Check the three words and try again.'
                ),
            },
            status=400,
        )

    return JsonResponse(
        {
            'success': True,
            **result,
        }
    )


def report_list(request):
    """Display public tree reports, newest first."""

    reports = TreeReport.objects.filter(
        visibility=TreeReport.Visibility.PUBLIC
    )

    return render(
        request,
        'reports/report_list.html',
        {'reports': reports},
    )


def report_map(request):
    """Display public tree reports on the Explore Map page."""

    reports = TreeReport.objects.filter(
        visibility=TreeReport.Visibility.PUBLIC
    ).select_related('owner')

    return render(
        request,
        'reports/report_map.html',
        {
            'reports': reports,
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
            'google_maps_map_id': settings.GOOGLE_MAPS_MAP_ID,
        },
    )


def report_detail(request, pk):
    """Display a public report or a private report to its owner."""

    report = get_object_or_404(TreeReport, pk=pk)

    if (
        report.visibility != TreeReport.Visibility.PUBLIC
        and report.owner != request.user
    ):
        raise Http404

    return render(
        request,
        'reports/report_detail.html',
        {'report': report},
    )


@login_required
def report_create(request):
    """Allow a logged-in user to submit a new tree report."""

    if request.method == 'POST':
        form = TreeReportForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            report = form.save(commit=False)
            report.owner = request.user

            three_word_address = convert_to_what3words(
                report.latitude,
                report.longitude,
            )

            if three_word_address:
                report.what3words = three_word_address

            report.save()

            messages.success(
                request,
                'Your tree report has been submitted successfully.'
            )

            if not three_word_address:
                messages.warning(
                    request,
                    (
                        'The report was saved, but the what3words '
                        'address could not be generated.'
                    )
                )

            return redirect(
                'reports:report_detail',
                pk=report.pk,
            )
    else:
        form = TreeReportForm()

    return render(
        request,
        'reports/report_form.html',
        {
            'form': form,
            'report': None,
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
            'google_maps_map_id': settings.GOOGLE_MAPS_MAP_ID,
        },
    )


@login_required
def report_edit(request, pk):
    """Allow only the report owner to edit their report."""

    report = get_object_or_404(
        TreeReport,
        pk=pk,
        owner=request.user,
    )

    existing_what3words = report.what3words

    if request.method == 'POST':
        form = TreeReportForm(
            request.POST,
            request.FILES,
            instance=report,
        )

        if form.is_valid():
            report = form.save(commit=False)

            three_word_address = convert_to_what3words(
                report.latitude,
                report.longitude,
            )

            if three_word_address:
                report.what3words = three_word_address
            else:
                report.what3words = existing_what3words

            report.save()

            messages.success(
                request,
                'Your tree report has been updated successfully.'
            )

            if not three_word_address:
                messages.warning(
                    request,
                    (
                        'The report was updated, but the what3words '
                        'address could not be refreshed.'
                    )
                )

            return redirect(
                'reports:report_detail',
                pk=report.pk,
            )
    else:
        form = TreeReportForm(instance=report)

    return render(
        request,
        'reports/report_form.html',
        {
            'form': form,
            'report': report,
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
            'google_maps_map_id': settings.GOOGLE_MAPS_MAP_ID,
        },
    )


@login_required
def report_delete(request, pk):
    """Allow only the report owner to delete their report."""

    report = get_object_or_404(
        TreeReport,
        pk=pk,
        owner=request.user,
    )

    if request.method == 'POST':
        report.delete()

        messages.success(
            request,
            'Your tree report has been deleted.'
        )

        return redirect('reports:report_list')

    return render(
        request,
        'reports/report_confirm_delete.html',
        {'report': report},
    )


@login_required
def progress_create(request, pk):
    """Allow a report owner to add a progress update."""

    report = get_object_or_404(
        TreeReport,
        pk=pk,
        owner=request.user,
    )

    if request.method == 'POST':
        form = ProgressUpdateForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():
            update = form.save(commit=False)
            update.tree_report = report
            update.author = request.user
            update.save()

            if update.status:
                report.status = update.status
                report.save(
                    update_fields=[
                        'status',
                        'updated_at',
                    ]
                )

            messages.success(
                request,
                'Progress update added successfully.'
            )

            return redirect(
                'reports:report_detail',
                pk=report.pk,
            )
    else:
        form = ProgressUpdateForm()

    return render(
        request,
        'reports/progress_form.html',
        {
            'form': form,
            'report': report,
            'update': None,
        },
    )


@login_required
def progress_edit(request, pk):
    """Allow only the update author to edit a progress update."""

    update = get_object_or_404(
        ProgressUpdate,
        pk=pk,
        author=request.user,
    )

    report = update.tree_report

    if request.method == 'POST':
        form = ProgressUpdateForm(
            request.POST,
            request.FILES,
            instance=update,
        )

        if form.is_valid():
            update = form.save()

            if update.status:
                report.status = update.status
                report.save(
                    update_fields=[
                        'status',
                        'updated_at',
                    ]
                )

            messages.success(
                request,
                'Progress update changed successfully.'
            )

            return redirect(
                'reports:report_detail',
                pk=report.pk,
            )
    else:
        form = ProgressUpdateForm(
            instance=update
        )

    return render(
        request,
        'reports/progress_form.html',
        {
            'form': form,
            'report': report,
            'update': update,
        },
    )


@login_required
def progress_delete(request, pk):
    """Allow only the update author to delete a progress update."""

    update = get_object_or_404(
        ProgressUpdate,
        pk=pk,
        author=request.user,
    )

    report = update.tree_report

    if request.method == 'POST':
        update.delete()

        latest_update = (
            report.progress_updates
            .exclude(status='')
            .first()
        )

        if latest_update:
            report.status = latest_update.status
        else:
            report.status = TreeReport.Status.ACTIVE

        report.save(
            update_fields=[
                'status',
                'updated_at',
            ]
        )

        messages.success(
            request,
            'Progress update deleted.'
        )

        return redirect(
            'reports:report_detail',
            pk=report.pk,
        )

    return render(
        request,
        'reports/progress_confirm_delete.html',
        {
            'update': update,
            'report': report,
        },
    )