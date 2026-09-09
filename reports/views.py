from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import TreeReportForm
from .models import TreeReport


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


def report_detail(request, pk):
    """Display one public tree report and its progress history."""

    report = get_object_or_404(
        TreeReport,
        pk=pk,
        visibility=TreeReport.Visibility.PUBLIC,
    )

    return render(
        request,
        'reports/report_detail.html',
        {'report': report},
    )


@login_required
def report_create(request):
    """Allow a logged-in user to submit a new tree report."""

    if request.method == 'POST':
        form = TreeReportForm(request.POST, request.FILES)

        if form.is_valid():
            report = form.save(commit=False)
            report.owner = request.user
            report.save()

            messages.success(
                request,
                'Your tree report has been submitted successfully.'
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
        {'form': form},
    )